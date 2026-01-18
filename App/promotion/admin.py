"""
Admin configuration for Promotion app.
"""

from django.contrib import admin
from .models import PromotionRule, PromotionRecord, PromotionAudit


@admin.register(PromotionRule)
class PromotionRuleAdmin(admin.ModelAdmin):
    list_display = ['school', 'class_obj', 'academic_year', 'pass_mark', 'rule_type', 'is_active']
    list_filter = ['school', 'academic_year', 'rule_type', 'is_active']


@admin.register(PromotionRecord)
class PromotionRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'from_class', 'to_class', 'academic_year', 'decision', 'is_automatic']
    list_filter = ['school', 'academic_year', 'decision', 'is_automatic']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(PromotionAudit)
class PromotionAuditAdmin(admin.ModelAdmin):
    list_display = ['promotion_record', 'action', 'changed_by', 'changed_at']
    readonly_fields = ['promotion_record', 'action', 'old_values', 'new_values', 'changed_by', 'changed_at']
