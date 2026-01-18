"""
Exam and Grading models for the SMS system.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from core.models import BaseModel, School


class GradeScale(BaseModel):
    """
    Grading scale for a section of the school.
    Section-based (Primary uses D1-D9, Pre-Primary uses A-F).
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='grade_scales')
    section = models.ForeignKey('schools.Section', on_delete=models.PROTECT, related_name='grade_scales')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['school', 'name']
        ordering = ['section', 'name']

    def __str__(self):
        return f"{self.school.acronym} - {self.name}"


class GradeLevel(BaseModel):
    """
    Individual grade level within a grading scale.
    """
    grade_scale = models.ForeignKey(
        GradeScale,
        on_delete=models.CASCADE,
        related_name='grade_levels'
    )
    grade = models.CharField(max_length=10, help_text="e.g., D1, C3, A, B")
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    description = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['grade_scale', 'order', 'min_score']

    def __str__(self):
        return f"{self.grade_scale.name} - {self.grade} ({self.min_score}-{self.max_score})"

    def clean(self):
        """Validate grade level score range."""
        if self.min_score > self.max_score:
            raise ValidationError('Minimum score cannot exceed maximum score.')


class ExamSet(BaseModel):
    """
    Group of exams (e.g., Mid Term Tests, End of Term Exams).
    Exam Sets are class-specific and term-specific.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exam_sets')
    class_obj = models.ForeignKey(
        'academic.Class',
        on_delete=models.CASCADE,
        related_name='exam_sets'
    )
    term = models.ForeignKey(
        'schools.Term',
        on_delete=models.CASCADE,
        related_name='exam_sets'
    )
    name = models.CharField(max_length=100, help_text="e.g., Mid Term Tests, End of Term Exams")
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-term', 'start_date']

    def __str__(self):
        return f"{self.class_obj.name} - {self.name}"


class Exam(BaseModel):
    """
    Individual exam within an exam set.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exams')
    exam_set = models.ForeignKey(
        ExamSet,
        on_delete=models.CASCADE,
        related_name='exams'
    )
    subject = models.ForeignKey(
        'academic.Subject',
        on_delete=models.CASCADE,
        related_name='exams'
    )
    max_score = models.IntegerField(default=100)
    passing_score = models.IntegerField(default=40)
    is_marked = models.BooleanField(
        default=True,
        help_text="If False, only grade is entered (no numeric marks)"
    )
    exam_date = models.DateField()
    duration_minutes = models.IntegerField(default=60)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['exam_date', 'subject']

    def __str__(self):
        return f"{self.exam_set.name} - {self.subject.name}"

    def clean(self):
        """Validate exam configuration."""
        if self.max_score <= 0:
            raise ValidationError('Maximum score must be positive.')
        if self.passing_score > self.max_score:
            raise ValidationError('Passing score cannot exceed maximum score.')


class Result(BaseModel):
    """
    Student exam result.
    Cannot exist without an Exam.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='results'
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='results'
    )
    marks = models.IntegerField(null=True, blank=True, help_text="Numeric marks (0-max_score)")
    grade = models.ForeignKey(
        GradeLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results'
    )
    custom_grade = models.CharField(max_length=10, blank=True, help_text="Manual grade entry")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    remarks = models.TextField(blank=True)
    entered_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results_entered'
    )
    approved_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results_approved'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['exam', 'student']
        indexes = [
            models.Index(fields=['exam', 'status']),
            models.Index(fields=['student', 'exam']),
        ]

    def __str__(self):
        return f"{self.student} - {self.exam.subject}: {self.marks or self.custom_grade}"

    def clean(self):
        """Validate result data."""
        if self.marks is not None:
            if self.marks < 0 or self.marks > self.exam.max_score:
                raise ValidationError(f'Marks must be between 0 and {self.exam.max_score}.')

    def calculate_grade(self):
        """Auto-calculate grade based on marks."""
        if self.marks is None:
            return None

        grade_scale = self.exam.grade_scale
        if not grade_scale:
            return None

        grade = GradeLevel.objects.filter(
            grade_scale=grade_scale,
            min_score__lte=self.marks,
            max_score__gte=self.marks
        ).first()
        return grade

    def save(self, *args, **kwargs):
        """Auto-calculate grade when marks are entered."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new or not self.grade:
            auto_grade = self.calculate_grade()
            if auto_grade and not self.custom_grade:
                self.grade = auto_grade
                super().save(update_fields=['grade'])


class ResultHistory(BaseModel):
    """
    Historical record of result changes.
    Fully audited - tracks all edits after creation.
    """
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_marks = models.IntegerField(null=True, blank=True)
    new_marks = models.IntegerField(null=True, blank=True)
    old_grade_id = models.IntegerField(null=True, blank=True)
    new_grade_id = models.IntegerField(null=True, blank=True)
    old_status = models.CharField(max_length=20, choices=Result.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Result.STATUS_CHOICES)
    changed_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True
    )
    change_reason = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"Change to {self.result} at {self.changed_at}"
