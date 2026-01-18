"""
Serializers for Exams app.
"""

from rest_framework import serializers
from .models import GradeScale, GradeLevel, ExamSet, Exam, Result


class GradeScaleSerializer(serializers.ModelSerializer):
    """Serializer for GradeScale model."""
    class Meta:
        model = GradeScale
        fields = [
            'id', 'school', 'section', 'name', 'description',
            'is_default', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class GradeLevelSerializer(serializers.ModelSerializer):
    """Serializer for GradeLevel model."""
    class Meta:
        model = GradeLevel
        fields = ['id', 'grade_scale', 'grade', 'min_score', 'max_score', 'description', 'order']


class ExamSetSerializer(serializers.ModelSerializer):
    """Serializer for ExamSet model."""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)

    class Meta:
        model = ExamSet
        fields = [
            'id', 'school', 'class_obj', 'class_name', 'term', 'term_name',
            'name', 'description', 'start_date', 'end_date',
            'is_published', 'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['published_at', 'created_at', 'updated_at']


class ExamSerializer(serializers.ModelSerializer):
    """Serializer for Exam model."""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    exam_set_name = serializers.CharField(source='exam_set.name', read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'school', 'exam_set', 'exam_set_name', 'subject', 'subject_name',
            'max_score', 'passing_score', 'is_marked', 'exam_date',
            'duration_minutes', 'instructions', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ResultSerializer(serializers.ModelSerializer):
    """Serializer for Result model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='exam.subject.name', read_only=True)
    exam_name = serializers.CharField(source='exam.exam_set.name', read_only=True)

    class Meta:
        model = Result
        fields = [
            'id', 'school', 'student', 'student_name', 'exam', 'exam_name',
            'subject_name', 'marks', 'grade', 'custom_grade', 'status',
            'remarks', 'entered_by', 'approved_by', 'approved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['entered_by', 'approved_by', 'approved_at', 'created_at', 'updated_at']
