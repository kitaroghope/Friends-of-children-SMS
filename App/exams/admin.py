"""
Admin configuration for Exams app.
"""

from django.contrib import admin
from .models import GradeScale, GradeLevel, ExamSet, Exam, Result, ResultHistory


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ['school', 'section', 'name', 'is_default', 'is_active']
    list_filter = ['school', 'section', 'is_default', 'is_active']


@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = ['grade_scale', 'grade', 'min_score', 'max_score', 'description']
    list_filter = ['grade_scale']


@admin.register(ExamSet)
class ExamSetAdmin(admin.ModelAdmin):
    list_display = ['school', 'class_obj', 'term', 'name', 'start_date', 'end_date', 'is_published']
    list_filter = ['school', 'term', 'is_published']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['exam_set', 'subject', 'max_score', 'passing_score', 'exam_date', 'is_marked']
    list_filter = ['school', 'exam_set', 'is_marked']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'marks', 'grade', 'status', 'entered_by']
    list_filter = ['school', 'exam', 'status']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(ResultHistory)
class ResultHistoryAdmin(admin.ModelAdmin):
    list_display = ['result', 'old_marks', 'new_marks', 'changed_by', 'changed_at']
    readonly_fields = ['result', 'old_marks', 'new_marks', 'changed_by', 'changed_at']
