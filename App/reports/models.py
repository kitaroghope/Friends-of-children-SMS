"""
Reports app for the SMS system.
Contains report configuration and generated report storage.
"""

from django.db import models
from django.core.exceptions import ValidationError
from core.models import BaseModel, School


class ReportDefinition(BaseModel):
    """
    Report configuration and definition.
    """
    TYPE_CHOICES = [
        ('academic_term', 'Termly Academic Report'),
        ('student_progress', 'Student Progress Report'),
        ('class_performance', 'Class Performance Summary'),
        ('parent_statement', 'Parent Financial Statement'),
        ('outstanding_balances', 'Outstanding Balances'),
        ('expected_fees', 'Next Term Expected Fees'),
        ('attendance', 'Attendance Report'),
        ('custom', 'Custom Report'),
    ]

    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
        ('html', 'HTML'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='report_definitions')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='pdf')
    template_name = models.CharField(max_length=100, blank=True)
    parameters = models.JSONField(
        null=True,
        blank=True,
        help_text="Report parameters configuration"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.school.acronym} - {self.name}"


class GeneratedReport(BaseModel):
    """
    Generated report instance.
    """
    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='generated_reports')
    report_definition = models.ForeignKey(
        ReportDefinition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports'
    )
    report_type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    parameters = models.JSONField(null=True, blank=True)
    file = models.FileField(upload_to='reports/%Y/%m/', null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    generated_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_generated'
    )
    error_message = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.status}"

    def save(self, *args, **kwargs):
        """Set file size when file is saved."""
        if self.file and self.pk:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class ReportSchedule(BaseModel):
    """
    Scheduled report generation.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('termly', 'Termly'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='report_schedules')
    report_definition = models.ForeignKey(
        ReportDefinition,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    recipients = models.JSONField(help_text="List of email addresses")
    parameters = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.frequency})"
