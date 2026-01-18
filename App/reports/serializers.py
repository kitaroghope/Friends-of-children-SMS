"""
Serializers for Reports app.
"""

from rest_framework import serializers
from .models import ReportDefinition, GeneratedReport, ReportSchedule


class ReportDefinitionSerializer(serializers.ModelSerializer):
    """Serializer for ReportDefinition model."""
    class Meta:
        model = ReportDefinition
        fields = [
            'id', 'school', 'name', 'description', 'report_type',
            'format', 'template_name', 'parameters', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class GeneratedReportSerializer(serializers.ModelSerializer):
    """Serializer for GeneratedReport model."""
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)

    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'school', 'report_definition', 'report_type', 'title',
            'parameters', 'file', 'file_size', 'status', 'generated_by',
            'generated_by_name', 'error_message', 'expires_at',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['file_size', 'status', 'generated_by', 'error_message', 'created_at', 'completed_at']


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializer for ReportSchedule model."""
    report_name = serializers.CharField(source='report_definition.name', read_only=True)

    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'school', 'report_definition', 'report_name', 'name',
            'frequency', 'recipients', 'parameters', 'is_active',
            'last_run_at', 'next_run_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['last_run_at', 'created_at', 'updated_at']
