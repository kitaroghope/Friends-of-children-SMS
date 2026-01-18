"""
Admin configuration for Offline app.
"""

from django.contrib import admin
from .models import SyncQueue, SyncLog, ConflictRecord, SyncBatch


@admin.register(SyncQueue)
class SyncQueueAdmin(admin.ModelAdmin):
    list_display = ['staff', 'action_type', 'status', 'created_offline_at', 'synced_at', 'retry_count']
    list_filter = ['school', 'status', 'action_type']
    search_fields = ['staff__first_name', 'staff__last_name']
    readonly_fields = ['created_offline_at', 'synced_at', 'processed_at']


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['sync_queue', 'result', 'processed_at', 'processed_by']
    list_filter = ['result']


@admin.register(ConflictRecord)
class ConflictRecordAdmin(admin.ModelAdmin):
    list_display = ['sync_queue', 'conflict_type', 'resolution', 'resolved_by', 'resolved_at']
    list_filter = ['conflict_type', 'resolution']
    readonly_fields = ['resolved_at']


@admin.register(SyncBatch)
class SyncBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_id', 'school', 'status', 'total_items', 'processed_items', 'failed_items', 'started_at']
    list_filter = ['school', 'status']
    readonly_fields = ['started_at', 'completed_at']
