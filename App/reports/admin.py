"""
Admin configuration for Reports app.
"""

from django.contrib import admin
from .models import ReportDefinition, GeneratedReport, ReportSchedule


@admin.register(ReportDefinition)
class ReportDefinitionAdmin(admin.ModelAdmin):
    list_display = ['school', 'name', 'report_type', 'format', 'is_active']
    list_filter = ['school', 'report_type', 'format', 'is_active']


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'status', 'generated_by', 'created_at', 'completed_at']
    list_filter = ['school', 'report_type', 'status']
    readonly_fields = ['created_at', 'completed_at']


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ['school', 'name', 'report_definition', 'frequency', 'is_active', 'next_run_at']
    list_filter = ['school', 'frequency', 'is_active']
