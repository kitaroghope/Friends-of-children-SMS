"""
Serializers for Academic app.
"""

from rest_framework import serializers
from .models import Class, Subject, ClassSubject, TeachingAssignment


class ClassSerializer(serializers.ModelSerializer):
    """Serializer for Class model."""
    section_name = serializers.CharField(source='section.name', read_only=True)
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = [
            'id', 'school', 'section', 'section_name', 'name', 'display_name',
            'capacity', 'order', 'is_active', 'students_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_students_count(self, obj):
        from students.models import Enrollment
        from schools.models import AcademicYear
        current_year = AcademicYear.objects.filter(school=obj.school, is_current=True).first()
        if current_year:
            return obj.enrollments.filter(academic_year=current_year, is_active=True).count()
        return 0


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model."""
    classes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = [
            'id', 'school', 'name', 'code', 'is_compulsory',
            'is_active', 'classes_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_classes_count(self, obj):
        return obj.class_subjects.filter(is_active=True).count()


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
