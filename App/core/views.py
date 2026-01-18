"""
Views for Core app.
"""

from rest_framework import viewsets, permissions
from .models import School, AuditLog
from .serializers import SchoolSerializer, AuditLogSerializer


class SchoolViewSet(viewsets.ModelViewSet):
    """
    ViewSet for School model.
    """
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter schools based on user's school access."""
        user = self.request.user
        if user.is_superuser:
            return School.objects.all()
        if hasattr(user, 'staff_profile'):
            return School.objects.filter(id=user.staff_profile.school.id)
        if hasattr(user, 'parent_profile'):
            return School.objects.filter(id=user.parent_profile.school.id)
        return School.objects.none()


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for AuditLog model (read-only).
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter audit logs based on user's school access."""
        user = self.request.user
        if user.is_superuser:
            return AuditLog.objects.all()
        if hasattr(user, 'staff_profile'):
            return AuditLog.objects.filter(school=user.staff_profile.school)
        return AuditLog.objects.none()
