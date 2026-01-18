"""
Serializers for Students app.
"""

from rest_framework import serializers
from .models import Student, Enrollment


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'school', 'student_number', 'first_name', 'last_name',
            'middle_name', 'full_name', 'gender', 'date_of_birth',
            'place_of_birth', 'nationality', 'religion', 'blood_group',
            'status', 'admission_date', 'exit_date', 'exit_reason',
            'photo', 'medical_notes', 'special_needs', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_name', 'class_obj', 'class_name',
            'academic_year', 'term', 'roll_number', 'admission_number',
            'is_active', 'enrollment_date', 'exit_date', 'exit_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
