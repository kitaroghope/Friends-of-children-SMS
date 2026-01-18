"""
Promotion models for the SMS system.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from core.models import BaseModel, School


class PromotionRule(BaseModel):
    """
    Configurable promotion rules per class per academic year.
    Policy-driven, allows different rules for different classes.
    """
    RULE_TYPE_CHOICES = [
        ('LAST_SET_ONLY', 'Use Last Exam Set Only'),
        ('SELECTED_SETS', 'Use Selected Exam Sets'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='promotion_rules')
    class_obj = models.ForeignKey(
        'academic.Class',
        on_delete=models.CASCADE,
        related_name='promotion_rules'
    )
    academic_year = models.ForeignKey(
        'schools.AcademicYear',
        on_delete=models.CASCADE,
        related_name='promotion_rules'
    )
    pass_mark = models.IntegerField(
        default=40,
        help_text="Minimum percentage required to pass"
    )
    rule_type = models.CharField(
        max_length=20,
        choices=RULE_TYPE_CHOICES,
        default='LAST_SET_ONLY'
    )
    selected_exam_sets = models.JSONField(
        null=True,
        blank=True,
        help_text="List of exam set IDs to use when rule_type is SELECTED_SETS"
    )
    require_all_compulsory = models.BooleanField(
        default=True,
        help_text="Student must pass all compulsory subjects"
    )
    allow_manual_override = models.BooleanField(
        default=True,
        help_text="Allow manual promotion decision override"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['school', 'class_obj', 'academic_year']
        ordering = ['academic_year', 'class_obj']

    def __str__(self):
        return f"{self.class_obj.name} - {self.academic_year} (Pass: {self.pass_mark}%)"

    def clean(self):
        """Validate promotion rule configuration."""
        if self.pass_mark < 0 or self.pass_mark > 100:
            raise ValidationError('Pass mark must be between 0 and 100.')
        if self.rule_type == 'SELECTED_SETS' and not self.selected_exam_sets:
            raise ValidationError('Selected exam sets are required for SELECTED_SETS rule type.')


class PromotionRecord(BaseModel):
    """
    Individual student promotion record.
    Records both automatic and manual promotion decisions.
    """
    DECISION_CHOICES = [
        ('promoted', 'Promoted'),
        ('retained', 'Retained'),
        ('withdrawn', 'Withdrawn'),
    ]

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='promotion_records'
    )
    from_class = models.ForeignKey(
        'academic.Class',
        on_delete=models.CASCADE,
        related_name='promotion_from'
    )
    to_class = models.ForeignKey(
        'academic.Class',
        on_delete=models.CASCADE,
        related_name='promotion_to',
        null=True,
        blank=True
    )
    academic_year = models.ForeignKey(
        'schools.AcademicYear',
        on_delete=models.CASCADE,
        related_name='promotion_records'
    )
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    is_automatic = models.BooleanField(
        default=False,
        help_text="True if decision was made by system, False if manual"
    )
    average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    total_marks = models.IntegerField(null=True, blank=True)
    subjects_passed = models.IntegerField(default=0)
    subjects_failed = models.IntegerField(default=0)
    reason = models.TextField(
        blank=True,
        help_text="Reason for decision, especially for manual overrides"
    )
    decided_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='promotions_decided'
    )
    decided_at = models.DateTimeField(auto_now_add=True)
    requires_review = models.BooleanField(
        default=False,
        help_text="True if missing exams require manual review"
    )
    review_notes = models.TextField(blank=True)
    is_final = models.BooleanField(
        default=False,
        help_text="True if promotion is final and cannot be changed"
    )

    class Meta:
        ordering = ['academic_year', 'student']

    def __str__(self):
        return f"{self.student} - {self.decision} ({self.academic_year})"


class PromotionAudit(BaseModel):
    """
    Audit trail for promotion decisions.
    """
    promotion_record = models.ForeignKey(
        PromotionRecord,
        on_delete=models.CASCADE,
        related_name='audit_trail'
    )
    action = models.CharField(max_length=50)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    changed_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.action} on {self.promotion_record} at {self.changed_at}"
