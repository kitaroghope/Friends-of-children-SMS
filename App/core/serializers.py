"""
Serializers for Core app.
"""

from rest_framework import serializers
from .models import School, AuditLog, SequenceNumber, Config


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for School model."""
    class Meta:
        model = School
        fields = [
            'id', 'name', 'acronym', 'address', 'phone', 'email',
            'currency', 'logo', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'school', 'school_name',
            'action', 'model_name', 'object_id', 'old_values',
            'new_values', 'ip_address', 'user_agent', 'timestamp',
            'is_offline', 'sync_batch_id'
        ]
        read_only_fields = fields


class SequenceNumberSerializer(serializers.ModelSerializer):
    """Serializer for SequenceNumber model."""
    class Meta:
        model = SequenceNumber
        fields = ['id', 'school', 'prefix', 'year', 'sequence', 'model_name']
        read_only_fields = ['sequence']


class ConfigSerializer(serializers.ModelSerializer):
    """Serializer for Config model."""
    school_name = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = Config
        fields = [
            'id', 'school', 'school_name', 'pass_mark_default',
            'promotion_rule_type', 'require_all_compulsory_for_promotion',
            'allow_manual_promotion_override', 'auto_approve_results',
            'invoice_group_by_parent', 'allow_overpayment',
            'require_refund_approval', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
