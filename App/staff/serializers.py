"""
Serializers for Staff app.
"""

from rest_framework import serializers
from .models import StaffProfile, StaffStatusHistory


class StaffProfileSerializer(serializers.ModelSerializer):
    """Serializer for StaffProfile model."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'user', 'school', 'staff_number', 'first_name', 'last_name',
            'full_name', 'gender', 'date_of_birth', 'phone', 'email',
            'address', 'department', 'position', 'status', 'date_joined',
            'date_left', 'emergency_contact', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class StaffStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for StaffStatusHistory model."""
    staff_name = serializers.CharField(source='staff.get_full_name', read_only=True)

    class Meta:
        model = StaffStatusHistory
        fields = [
            'id', 'staff', 'staff_name', 'old_status', 'new_status',
            'reason', 'effective_date', 'changed_by', 'created_at'
        ]
        read_only_fields = ['created_at']
