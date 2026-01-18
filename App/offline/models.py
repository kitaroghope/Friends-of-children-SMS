"""
Offline sync models for the SMS system.
Handles offline data entry and synchronization.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from core.models import BaseModel, School


class SyncQueue(BaseModel):
    """
    Queue for offline data entry.
    Offline entries are stored as queued actions.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('conflict', 'Conflict'),
    ]

    ACTION_TYPE_CHOICES = [
        ('create_student', 'Create Student'),
        ('update_student', 'Update Student'),
        ('create_result', 'Create Result'),
        ('update_result', 'Update Result'),
        ('create_payment', 'Create Payment'),
        ('update_payment', 'Update Payment'),
        ('create_enrollment', 'Create Enrollment'),
        ('update_enrollment', 'Update Enrollment'),
        ('custom', 'Custom Action'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='sync_queue')
    staff = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.CASCADE,
        related_name='sync_queue'
    )
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    payload = models.JSONField(help_text="Data payload for the action")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(default=0, help_text="Higher = processed first")
    created_offline_at = models.DateTimeField()
    synced_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    batch_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'created_offline_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['staff', 'status']),
            models.Index(fields=['batch_id']),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.status} (created: {self.created_offline_at})"

    def can_retry(self):
        """Check if action can be retried."""
        return self.retry_count < self.max_retries and self.status == 'rejected'

    def mark_processing(self):
        """Mark as processing."""
        self.status = 'processing'
        self.save(update_fields=['status'])

    def mark_completed(self):
        """Mark as completed."""
        self.status = 'completed'
        self.synced_at = timezone.now()
        self.save(update_fields=['status', 'synced_at'])

    def mark_rejected(self, error_message):
        """Mark as rejected with error message."""
        self.status = 'rejected'
        self.error_message = error_message
        self.retry_count += 1
        self.save(update_fields=['status', 'error_message', 'retry_count', 'updated_at'])


class SyncLog(BaseModel):
    """
    Log of sync operations.
    """
    RESULT_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
        ('conflict', 'Conflict'),
    ]

    sync_queue = models.ForeignKey(
        SyncQueue,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    error_message = models.TextField(blank=True)
    response_data = models.JSONField(null=True, blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        ordering = ['-processed_at']

    def __str__(self):
        return f"{self.sync_queue} - {self.result} at {self.processed_at}"


class ConflictRecord(BaseModel):
    """
    Record of sync conflicts requiring resolution.
    """
    RESOLUTION_CHOICES = [
        ('server_wins', 'Server Wins'),
        ('client_wins', 'Client Wins'),
        ('manual', 'Manual Resolution'),
        ('merged', 'Merged'),
    ]

    sync_queue = models.ForeignKey(
        SyncQueue,
        on_delete=models.CASCADE,
        related_name='conflicts'
    )
    conflict_type = models.CharField(max_length=100)
    server_data = models.JSONField(null=True, blank=True)
    client_data = models.JSONField(null=True, blank=True)
    resolution = models.CharField(
        max_length=20,
        choices=RESOLUTION_CHOICES,
        null=True,
        blank=True
    )
    resolved_data = models.JSONField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conflicts_resolved'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Conflict: {self.conflict_type} at {self.created_at}"

    def is_resolved(self):
        """Check if conflict has been resolved."""
        return self.resolution is not None


class SyncBatch(BaseModel):
    """
    Batch of sync operations.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='sync_batches')
    batch_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    device_id = models.CharField(max_length=100, blank=True)
    total_items = models.IntegerField(default=0)
    processed_items = models.IntegerField(default=0)
    failed_items = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Batch {self.batch_id} - {self.status}"

    def update_progress(self, success=True):
        """Update batch progress."""
        self.processed_items += 1
        if not success:
            self.failed_items += 1
        if self.processed_items >= self.total_items:
            self.status = 'completed' if self.failed_items == 0 else 'failed'
            self.completed_at = timezone.now()
        self.save(update_fields=['processed_items', 'failed_items', 'status', 'completed_at'])


# Import timezone for use in model methods
from django.utils import timezone
