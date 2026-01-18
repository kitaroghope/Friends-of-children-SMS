"""
Serializers for Academic app.
"""

from rest_framework import serializers
from .models import Class, Subject, ClassSubject, TeachingAssignment


class ClassSerializer(serializers.ModelSerializer):
    """Serializer for Class model."""
    section_name = serializers.CharField(source='section.name', read_only=True)

    class Meta:
        model = Class
        fields = [
            'id', 'school', 'section', 'section_name', 'name', 'display_name',
            'capacity', 'order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model."""
    class Meta:
        model = Subject
        fields = [
            'id', 'school', 'name', 'code', 'is_compulsory',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ClassSubjectSerializer(serializers.ModelSerializer):
    """Serializer for ClassSubject model."""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = ClassSubject
        fields = [
            'id', 'school', 'class_obj', 'class_name', 'subject', 'subject_name',
            'is_compulsory', 'max_score', 'weekly_periods',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TeachingAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for TeachingAssignment model."""
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = TeachingAssignment
        fields = [
            'id', 'school', 'teacher', 'teacher_name', 'class_obj', 'class_name',
            'subject', 'subject_name', 'academic_year', 'term',
            'start_date', 'end_date', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
