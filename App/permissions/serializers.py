"""
Serializers for Permissions app.
"""

from rest_framework import serializers
from .models import Permission, Role, RolePermission, StaffRole


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model."""
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'description', 'category']
        read_only_fields = ['id']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    permission_codes = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            'id', 'school', 'name', 'description', 'is_active',
            'permission_codes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_permission_codes(self, obj):
        return list(obj.permissions.values_list('code', flat=True))


class StaffRoleSerializer(serializers.ModelSerializer):
    """Serializer for StaffRole model."""
    role_name = serializers.CharField(source='role.name', read_only=True)
    staff_name = serializers.CharField(source='staff.get_full_name', read_only=True)

    class Meta:
        model = StaffRole
        fields = [
            'id', 'staff', 'staff_name', 'role', 'role_name',
            'is_active', 'granted_at', 'granted_by', 'expires_at'
        ]
        read_only_fields = ['granted_at']
