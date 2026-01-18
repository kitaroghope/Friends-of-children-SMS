"""
School and Academic Year models.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel, School


class AcademicYear(BaseModel):
    """
    Represents an academic year in a school.
    Each academic year contains exactly 3 terms.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='academic_years')
    year = models.IntegerField(help_text="e.g., 2025 for 2025-2026")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ['school', 'year']
        ordering = ['-year']

    def __str__(self):
        return f"{self.school.acronym} - {self.year}/{self.year + 1}"

    def clean(self):
        """Validate that end_date is after start_date."""
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise models.ValidationError('End date must be after start date.')

    def save(self, *args, **kwargs):
        """Ensure only one current academic year per school."""
        if self.is_current:
            AcademicYear.objects.filter(
                school=self.school, is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Term(BaseModel):
    """
    Represents a term within an academic year.
    Each academic year has exactly 3 terms.
    """
    TERM_CHOICES = [
        (1, 'Term 1'),
        (2, 'Term 2'),
        (3, 'Term 3'),
    ]

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='terms'
    )
    term_number = models.IntegerField(choices=TERM_CHOICES, validators=[
        MinValueValidator(1), MaxValueValidator(3)
    ])
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['academic_year', 'term_number']
        ordering = ['academic_year', 'term_number']

    def __str__(self):
        return f"{self.academic_year} - {self.get_term_number_display()}"

    def clean(self):
        """Validate term dates are within academic year."""
        if self.end_date and self.start_date:
            if self.end_date <= self.start_date:
                raise models.ValidationError('End date must be after start date.')
            if self.academic_year:
                if self.start_date < self.academic_year.start_date:
                    raise models.ValidationError(
                        'Term start date must be within academic year.'
                    )
                if self.end_date > self.academic_year.end_date:
                    raise models.ValidationError(
                        'Term end date must be within academic year.'
                    )


class Section(BaseModel):
    """
    Represents a section of the school (Pre-Primary, Primary, etc.).
    """
    SECTION_CHOICES = [
        ('pre_primary', 'Pre-Primary'),
        ('primary', 'Primary'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=50, choices=SECTION_CHOICES)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ['school', 'name']
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.school.acronym} - {self.get_name_display()}"
