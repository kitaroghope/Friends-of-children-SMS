"""
Serializers for Schools app.
"""

from rest_framework import serializers
from .models import AcademicYear, Term, Section


class AcademicYearSerializer(serializers.ModelSerializer):
    """Serializer for AcademicYear model."""
    class Meta:
        model = AcademicYear
        fields = [
            'id', 'school', 'year', 'start_date', 'end_date',
            'is_current', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TermSerializer(serializers.ModelSerializer):
    """Serializer for Term model."""
    term_number_display = serializers.CharField(source='get_term_number_display', read_only=True)

    class Meta:
        model = Term
        fields = [
            'id', 'academic_year', 'term_number', 'term_number_display',
            'name', 'start_date', 'end_date', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for Section model."""
    name_display = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Section
        fields = [
            'id', 'school', 'name', 'name_display', 'description',
            'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
