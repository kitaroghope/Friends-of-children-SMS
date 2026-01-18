"""
Academic structure models: Class, Subject, TeachingAssignment.
"""

from django.db import models
from django.core.exceptions import ValidationError
from core.models import BaseModel, School


class Class(BaseModel):
    """
    Represents a class in a school (e.g., P1, P2, P3, etc.).
    Each class belongs to a section.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    section = models.ForeignKey('schools.Section', on_delete=models.PROTECT, related_name='classes')
    name = models.CharField(max_length=50, help_text="e.g., P1, P2, P3, Nursery, Baby")
    display_name = models.CharField(max_length=100, blank=True)
    capacity = models.IntegerField(default=40)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['school', 'name']
        ordering = ['section', 'order', 'name']

    def __str__(self):
        return f"{self.school.acronym} - {self.name}"

    def clean(self):
        """Validate class belongs to school's section."""
        if self.section.school != self.school:
            raise ValidationError('Class must belong to the same school as its section.')


class Subject(BaseModel):
    """
    Represents a subject in the curriculum.
    Subjects can be compulsory or optional.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    is_compulsory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.school.acronym} - {self.name}"


class ClassSubject(BaseModel):
    """
    Represents the assignment of a subject to a class.
    Allows for class-specific subject configuration.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='class_subjects')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_subjects')
    is_compulsory = models.BooleanField(default=True)
    max_score = models.IntegerField(default=100)
    weekly_periods = models.IntegerField(default=1)

    class Meta:
        unique_together = ['school', 'class_obj', 'subject']
        ordering = ['class_obj', 'subject']

    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name}"


class TeachingAssignment(BaseModel):
    """
    Represents a teacher's assignment to teach a subject in a class.
    Time-bound assignment with optional term specificity.
    Critical: Exams and Results NEVER reference teachers directly.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teaching_assignments')
    teacher = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.CASCADE,
        related_name='teaching_assignments'
    )
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='teaching_assignments'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='teaching_assignments'
    )
    academic_year = models.ForeignKey(
        'schools.AcademicYear',
        on_delete=models.CASCADE,
        related_name='teaching_assignments'
    )
    term = models.ForeignKey(
        'schools.Term',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='teaching_assignments',
        help_text="Leave blank for full-year assignment"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['academic_year', 'class_obj', 'subject']

    def __str__(self):
        term_str = f" - {self.term}" if self.term else ""
        return f"{self.teacher} teaches {self.subject} in {self.class_obj}{term_str}"

    def clean(self):
        """Validate teaching assignment dates."""
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError('End date must be after start date.')

        if self.academic_year:
            if self.start_date < self.academic_year.start_date:
                raise ValidationError('Start date must be within academic year.')
            if self.end_date and self.end_date > self.academic_year.end_date:
                raise ValidationError('End date must be within academic year.')

    def is_valid_for_date(self, date):
        """Check if assignment is valid for a specific date."""
        if date < self.start_date:
            return False
        if self.end_date and date > self.end_date:
            return False
        return self.is_active
