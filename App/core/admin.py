"""
Admin configuration for Core app.
"""

from django.contrib import admin
from .models import School, AuditLog, SequenceNumber, Config, SchoolRequest


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'acronym', 'currency', 'is_active', 'created_at']
    list_filter = ['is_active', 'currency']
    search_fields = ['name', 'acronym', 'email']
    ordering = ['name']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'action', 'model_name', 'timestamp', 'is_offline']
    list_filter = ['action', 'is_offline', 'timestamp']
    search_fields = ['model_name', 'object_id']
    readonly_fields = ['user', 'school', 'action', 'model_name', 'object_id',
                       'old_values', 'new_values', 'ip_address', 'user_agent',
                       'timestamp', 'is_offline', 'sync_batch_id']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'


@admin.register(SequenceNumber)
class SequenceNumberAdmin(admin.ModelAdmin):
    list_display = ['school', 'prefix', 'year', 'model_name', 'sequence']
    list_filter = ['school', 'model_name', 'year']
    readonly_fields = ['sequence']


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['school', 'pass_mark_default', 'promotion_rule_type',
                    'require_all_compulsory_for_promotion', 'auto_approve_results']
    fieldsets = (
        (None, {'fields': ('school',)}),
        ('Promotion Settings', {'fields': (
            'pass_mark_default', 'promotion_rule_type',
            'require_all_compulsory_for_promotion', 'allow_manual_promotion_override'
        )}),
        ('Result Settings', {'fields': ('auto_approve_results',)}),
        ('Finance Settings', {'fields': (
            'invoice_group_by_parent', 'allow_overpayment', 'require_refund_approval'
        )}),
    )


@admin.register(SchoolRequest)
class SchoolRequestAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'requester_name', 'requester_email',
                    'status', 'reviewed_by', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['school_name', 'requester_name', 'requester_email']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_by', 'reviewed_at']
    ordering = ['-created_at']

    actions = ['approve_requests', 'reject_requests']

    fieldsets = (
        ('Requester Information', {'fields': (
            'requester_name', 'requester_email', 'requester_phone'
        )}),
        ('School Information', {'fields': (
            'school_name', 'school_acronym', 'school_phone',
            'school_email', 'school_address', 'currency', 'notes'
        )}),
        ('Review', {'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def approve_requests(self, request, queryset):
        """Approve selected school requests."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} request(s) approved.')
    approve_requests.short_description = 'Approve selected requests'

    def reject_requests(self, request, queryset):
        """Reject selected school requests."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} request(s) rejected.')
    reject_requests.short_description = 'Reject selected requests'
