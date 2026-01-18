"""
Admin configuration for Parents app.
"""

from django.contrib import admin
from .models import ParentProfile, StudentParent


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'school', 'relationship', 'is_emergency_contact']
    list_filter = ['school', 'relationship', 'is_emergency_contact']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    ordering = ['school', 'last_name', 'first_name']


@admin.register(StudentParent)
class StudentParentAdmin(admin.ModelAdmin):
    list_display = ['student', 'parent', 'parent_type', 'is_primary', 'is_financial_responsible']
    list_filter = ['school', 'parent_type', 'is_primary', 'is_financial_responsible']
