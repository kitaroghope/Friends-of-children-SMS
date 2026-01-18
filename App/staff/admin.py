"""
Admin configuration for Staff app.
"""

from django.contrib import admin
from .models import StaffProfile, StaffStatusHistory


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['staff_number', 'first_name', 'last_name', 'school', 'status', 'date_joined']
    list_filter = ['school', 'status', 'department']
    search_fields = ['staff_number', 'first_name', 'last_name']
    ordering = ['school', 'last_name', 'first_name']


@admin.register(StaffStatusHistory)
class StaffStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['staff', 'old_status', 'new_status', 'effective_date', 'changed_by']
    list_filter = ['old_status', 'new_status']
    readonly_fields = ['staff', 'old_status', 'new_status', 'effective_date', 'changed_by']
