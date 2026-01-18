"""
Parent models for the SMS system.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models import BaseModel, School


class ParentProfile(BaseModel):
    """
    Represents a parent/guardian in the system.
    Parent phone number must be unique per school.
    A parent may also be a staff member.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_profile',
        null=True,
        blank=True
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='parents')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, help_text="Unique per school")
    alternate_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    relationship = models.CharField(
        max_length=50,
        choices=[
            ('father', 'Father'),
            ('mother', 'Mother'),
            ('guardian', 'Guardian'),
            ('other', 'Other'),
        ],
        default='father'
    )
    is_emergency_contact = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['school', 'phone']
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        """Return full name."""
        return f"{self.first_name} {self.last_name}"

    def get_children(self):
        """Return all children of this parent."""
        return Student.objects.filter(parents=self)

    def clean(self):
        """Validate phone uniqueness."""
        if self.phone:
            existing = ParentProfile.objects.filter(
                school=self.school,
                phone=self.phone
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError('This phone number is already registered in this school.')


class StudentParent(BaseModel):
    """
    Many-to-many relationship between students and parents.
    Allows tracking parent-student relationships with additional metadata.
    """
    PARENT_TYPE_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
        ('other', 'Other'),
    ]

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='student_parents'
    )
    parent = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        related_name='student_parents'
    )
    parent_type = models.CharField(max_length=20, choices=PARENT_TYPE_CHOICES, default='father')
    is_primary = models.BooleanField(default=False)
    can_receive_sms = models.BooleanField(default=True)
    can_pickup = models.BooleanField(default=False)
    is_financial_responsible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'parent']

    def __str__(self):
        return f"{self.parent} - {self.student}"
