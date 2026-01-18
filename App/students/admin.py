"""
Admin configuration for Students app.
"""

from django.contrib import admin
from .models import Student, Enrollment, StudentStatusHistory


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_number', 'first_name', 'last_name', 'school', 'status', 'admission_date']
    list_filter = ['school', 'status', 'gender']
    search_fields = ['student_number', 'first_name', 'last_name']
    ordering = ['school', 'last_name', 'first_name']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_obj', 'academic_year', 'term', 'is_active']
    list_filter = ['school', 'academic_year', 'is_active']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(StudentStatusHistory)
class StudentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['student', 'old_status', 'new_status', 'effective_date', 'changed_by']
    list_filter = ['old_status', 'new_status']
    readonly_fields = ['student', 'old_status', 'new_status', 'effective_date', 'changed_by']
