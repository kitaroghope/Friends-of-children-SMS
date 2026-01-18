"""
Admin configuration for Academic app.
"""

from django.contrib import admin
from .models import Class, Subject, ClassSubject, TeachingAssignment


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['school', 'name', 'section', 'capacity', 'order', 'is_active']
    list_filter = ['school', 'section', 'is_active']
    search_fields = ['name', 'display_name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['school', 'name', 'code', 'is_compulsory', 'is_active']
    list_filter = ['school', 'is_compulsory', 'is_active']
    search_fields = ['name', 'code']


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['school', 'class_obj', 'subject', 'is_compulsory', 'max_score']
    list_filter = ['school', 'class_obj', 'subject']


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(admin.ModelAdmin):
    list_display = ['school', 'teacher', 'class_obj', 'subject', 'academic_year', 'term', 'is_active']
    list_filter = ['school', 'academic_year', 'term', 'is_active']
    search_fields = ['teacher__first_name', 'teacher__last_name']
