"""
Views for Offline app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import SyncQueue, ConflictRecord, SyncBatch
from .serializers import SyncQueueSerializer, ConflictRecordSerializer, SyncBatchSerializer


class SyncQueueViewSet(viewsets.ModelViewSet):
    """ViewSet for SyncQueue model."""
    queryset = SyncQueue.objects.all()
    serializer_class = SyncQueueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return SyncQueue.objects.all()
        if hasattr(user, 'staff_profile'):
            return SyncQueue.objects.filter(school=user.staff_profile.school)
        return SyncQueue.objects.none()

    def sync_all(self, request):
        """Process all pending sync items."""
        pending = self.get_queryset().filter(status='pending')
        for item in pending:
            # Process sync item - simplified for now
            item.mark_completed()
        return Response({'processed': pending.count()})


class ConflictRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for ConflictRecord model."""
    queryset = ConflictRecord.objects.all()
    serializer_class = ConflictRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ConflictRecord.objects.all()
        if hasattr(user, 'staff_profile'):
            return ConflictRecord.objects.filter(school=user.staff_profile.school)
        return ConflictRecord.objects.none()


class SyncBatchViewSet(viewsets.ModelViewSet):
    """ViewSet for SyncBatch model."""
    queryset = SyncBatch.objects.all()
    serializer_class = SyncBatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return SyncBatch.objects.all()
        if hasattr(user, 'staff_profile'):
            return SyncBatch.objects.filter(school=user.staff_profile.school)
        return SyncBatch.objects.none()
