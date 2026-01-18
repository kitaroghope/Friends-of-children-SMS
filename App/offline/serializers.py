"""
Serializers for Offline app.
"""

from rest_framework import serializers
from .models import SyncQueue, SyncLog, ConflictRecord, SyncBatch


class SyncQueueSerializer(serializers.ModelSerializer):
    """Serializer for SyncQueue model."""
    staff_name = serializers.CharField(source='staff.get_full_name', read_only=True)

    class Meta:
        model = SyncQueue
        fields = [
            'id', 'school', 'staff', 'staff_name', 'action_type',
            'payload', 'status', 'priority', 'created_offline_at',
            'synced_at', 'processed_at', 'error_message', 'retry_count',
            'batch_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_offline_at', 'synced_at', 'processed_at', 'created_at', 'updated_at']


class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer for SyncLog model."""
    class Meta:
        model = SyncLog
        fields = ['id', 'sync_queue', 'result', 'error_message', 'response_data', 'processed_at', 'processed_by']


class ConflictRecordSerializer(serializers.ModelSerializer):
    """Serializer for ConflictRecord model."""
    staff_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)

    class Meta:
        model = ConflictRecord
        fields = [
            'id', 'sync_queue', 'conflict_type', 'server_data', 'client_data',
            'resolution', 'resolved_data', 'resolved_by', 'staff_name',
            'resolved_at', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class SyncBatchSerializer(serializers.ModelSerializer):
    """Serializer for SyncBatch model."""
    class Meta:
        model = SyncBatch
        fields = [
            'id', 'school', 'batch_id', 'status', 'device_id',
            'total_items', 'processed_items', 'failed_items',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = ['started_at', 'completed_at', 'created_at']
