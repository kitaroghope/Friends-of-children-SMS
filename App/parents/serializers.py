"""
Serializers for Parents app.
"""

from rest_framework import serializers
from .models import ParentProfile, StudentParent


class ParentProfileSerializer(serializers.ModelSerializer):
    """Serializer for ParentProfile model."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = ParentProfile
        fields = [
            'id', 'user', 'school', 'first_name', 'last_name', 'full_name',
            'phone', 'alternate_phone', 'email', 'address', 'occupation',
            'relationship', 'is_emergency_contact', 'notes', 'children_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_children_count(self, obj):
        return obj.student_parents.filter(is_active=True).count()


class StudentParentSerializer(serializers.ModelSerializer):
    """Serializer for StudentParent model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)
    first_name = serializers.CharField(source='parent.first_name', read_only=True)
    last_name = serializers.CharField(source='parent.last_name', read_only=True)
    phone = serializers.CharField(source='parent.phone', read_only=True)

    class Meta:
        model = StudentParent
        fields = [
            'id', 'student', 'student_name', 'parent', 'parent_name',
            'first_name', 'last_name', 'phone',
            'parent_type', 'is_primary', 'can_receive_sms', 'can_pickup',
            'is_financial_responsible', 'created_at'
        ]
        read_only_fields = ['created_at']
