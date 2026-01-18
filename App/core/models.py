"""
Core models for the SMS system.
Contains BaseModel, AuditLog, and utility mixins.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class School(models.Model):
    """
    Represents a school in the multi-school SMS system.
    All other models reference a school for data isolation.
    """
    name = models.CharField(max_length=200)
    acronym = models.CharField(max_length=10, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    currency = models.CharField(max_length=3, default='UGX')
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.acronym})"


class BaseModel(models.Model):
    """
    Abstract base model for all business models.
    Enforces school-level data isolation and audit trail.
    """
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )

    class Meta:
        abstract = True


class AuditLog(models.Model):
    """
    Immutable audit log for tracking all critical changes.
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('sync', 'Sync'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_offline = models.BooleanField(default=False)
    sync_batch_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['school', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.action} on {self.model_name} at {self.timestamp}"


class SequenceNumber(models.Model):
    """
    Manages unique number sequences per school/year.
    Used for generating student numbers, invoice numbers, etc.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    prefix = models.CharField(max_length=20)
    year = models.IntegerField()
    sequence = models.IntegerField(default=0)
    model_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ['school', 'prefix', 'year', 'model_name']

    def get_next_number(self):
        """Increment and return the next number in sequence."""
        self.sequence += 1
        self.save(update_fields=['sequence'])
        return self.sequence

    def __str__(self):
        return f"{self.prefix}/{self.year}/{self.model_name}: {self.sequence}"


class Config(models.Model):
    """
    School-specific configuration settings.
    Policy-driven, configurable per school.
    """
    school = models.OneToOneField(
        School,
        on_delete=models.CASCADE,
        related_name='config'
    )
    pass_mark_default = models.IntegerField(default=40)
    promotion_rule_type = models.CharField(
        max_length=20,
        default='LAST_SET_ONLY',
        choices=[
            ('LAST_SET_ONLY', 'Use Last Exam Set Only'),
            ('SELECTED_SETS', 'Use Selected Exam Sets'),
        ]
    )
    require_all_compulsory_for_promotion = models.BooleanField(default=True)
    allow_manual_promotion_override = models.BooleanField(default=True)
    auto_approve_results = models.BooleanField(default=False)
    invoice_group_by_parent = models.BooleanField(default=True)
    allow_overpayment = models.BooleanField(default=True)
    require_refund_approval = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Config for {self.school.name}"


class SchoolRequest(models.Model):
    """
    Pending school registration requests.
    Schools must be approved before they can be onboarded.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Requester info
    requester_name = models.CharField(max_length=200)
    requester_email = models.EmailField()
    requester_phone = models.CharField(max_length=20)

    # School info
    school_name = models.CharField(max_length=200)
    school_acronym = models.CharField(max_length=10)
    school_phone = models.CharField(max_length=20)
    school_email = models.EmailField()
    school_address = models.TextField()
    currency = models.CharField(max_length=3, default='UGX')
    notes = models.TextField(blank=True)

    # Review
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_school_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"School Request: {self.school_name} ({self.status})"
