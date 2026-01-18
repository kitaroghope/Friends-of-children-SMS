"""
Serializers for Promotion app.
"""

from rest_framework import serializers
from .models import PromotionRule, PromotionRecord, PromotionAudit


class PromotionRuleSerializer(serializers.ModelSerializer):
    """Serializer for PromotionRule model."""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)

    class Meta:
        model = PromotionRule
        fields = [
            'id', 'school', 'class_obj', 'class_name', 'academic_year',
            'pass_mark', 'rule_type', 'selected_exam_sets',
            'require_all_compulsory', 'allow_manual_override', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PromotionRecordSerializer(serializers.ModelSerializer):
    """Serializer for PromotionRecord model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    from_class_name = serializers.CharField(source='from_class.name', read_only=True)
    to_class_name = serializers.CharField(source='to_class.name', read_only=True)

    class Meta:
        model = PromotionRecord
        fields = [
            'id', 'student', 'student_name', 'from_class', 'from_class_name',
            'to_class', 'to_class_name', 'academic_year', 'decision',
            'is_automatic', 'average_score', 'total_marks',
            'subjects_passed', 'subjects_failed', 'reason',
            'decided_by', 'decided_at', 'requires_review', 'review_notes',
            'is_final', 'created_at'
        ]
        read_only_fields = ['decided_at', 'created_at']


class PromotionAuditSerializer(serializers.ModelSerializer):
    """Serializer for PromotionAudit model."""
    class Meta:
        model = PromotionAudit
        fields = [
            'id', 'promotion_record', 'action', 'old_values', 'new_values',
            'changed_by', 'changed_at'
        ]
        read_only_fields = ['changed_at']
