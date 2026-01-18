"""
Student models for the SMS system.
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models import BaseModel, School


class Student(BaseModel):
    """
    Represents a student in the system.
    Student numbers are reusable across years.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('transferred', 'Transferred'),
        ('dropped', 'Dropped'),
        ('suspended', 'Suspended'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        null=True,
        blank=True
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    student_number = models.CharField(max_length=20, help_text="Format: number/year/school_acronym")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=200, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    religion = models.CharField(max_length=100, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    admission_date = models.DateField(null=True, blank=True)
    exit_date = models.DateField(null=True, blank=True)
    exit_reason = models.TextField(blank=True)
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    medical_notes = models.TextField(blank=True)
    special_needs = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['school', 'student_number']
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['school', 'status']),
            models.Index(fields=['student_number']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_number})"

    def get_full_name(self):
        """Return full name."""
        parts = [self.first_name, self.middle_name, self.last_name]
        return ' '.join(p for p in parts if p)

    @property
    def current_class(self):
        """Get the student's current class enrollment."""
        from schools.models import AcademicYear
        current_year = AcademicYear.objects.filter(
            school=self.school, is_current=True
        ).first()
        if current_year:
            return self.enrollments.filter(
                academic_year=current_year,
                is_active=True
            ).select_related('class_obj').first()
        return None

    @property
    def current_parents(self):
        """Get the student's current parents."""
        return ParentProfile.objects.filter(
            school=self.school,
            student_parents__student=self,
            student_parents__is_active=True
        )

    def generate_student_number(self, year):
        """Generate a unique student number."""
        from core.models import SequenceNumber
        seq, _ = SequenceNumber.objects.get_or_create(
            school=self.school,
            prefix='STU',
            year=year,
            model_name='Student'
        )
        number = seq.get_next_number()
        return f"{number}/{year}/{self.school.acronym}"


class Enrollment(BaseModel):
    """
    Represents a student's enrollment in a class for an academic term.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    class_obj = models.ForeignKey(
        'academic.Class',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    academic_year = models.ForeignKey(
        'schools.AcademicYear',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    term = models.ForeignKey(
        'schools.Term',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='enrollments'
    )
    roll_number = models.CharField(max_length=10, blank=True)
    admission_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    enrollment_date = models.DateField(auto_now_add=True)
    exit_date = models.DateField(null=True, blank=True)
    exit_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'academic_year', 'class_obj']
        ordering = ['-academic_year', 'class_obj']

    def __str__(self):
        return f"{self.student} in {self.class_obj} ({self.academic_year})"


class StudentStatusHistory(BaseModel):
    """
    Historical record of student status changes.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(max_length=20, choices=Student.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Student.STATUS_CHOICES)
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
        return f"{self.student} changed from {self.old_status} to {self.new_status}"


# Import ParentProfile for foreign key reference
from parents.models import ParentProfile
