"""
Staff models for the SMS system.
"""

from django.db import models
from django.conf import settings
from core.models import BaseModel, School


class StaffProfile(BaseModel):
    """
    Represents a staff member in a school.
    Status changes preserve historical records.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='staff')
    staff_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    date_joined = models.DateField(null=True, blank=True)
    date_left = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['school', 'staff_number']
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.staff_number})"

    def get_full_name(self):
        """Return full name."""
        return f"{self.first_name} {self.last_name}"

    def is_active(self):
        """Check if staff member is active."""
        return self.status == 'active'

    def is_suspended(self):
        """Check if staff member is suspended."""
        return self.status == 'suspended'

    def suspend(self, reason=None):
        """Suspend the staff member."""
        self.status = 'suspended'
        self.save(update_fields=['status', 'updated_at'])

    def reactivate(self):
        """Reactivate the staff member."""
        self.status = 'active'
        self.save(update_fields=['status', 'updated_at'])

    def terminate(self, date_left=None):
        """Terminate the staff member."""
        self.status = 'terminated'
        self.date_left = date_left or self.date_left
        self.save(update_fields=['status', 'date_left', 'updated_at'])


class StaffStatusHistory(BaseModel):
    """
    Historical record of staff status changes.
    Preserves all status transitions.
    """
    staff = models.ForeignKey(
        StaffProfile,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(max_length=20, choices=StaffProfile.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=StaffProfile.STATUS_CHOICES)
    reason = models.TextField(blank=True)
    effective_date = models.DateField()
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        ordering = ['-effective_date', '-created_at']

    def __str__(self):
        return f"{self.staff} changed from {self.old_status} to {self.new_status}"
