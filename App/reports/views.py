"""
Views for Reports app.
"""

from rest_framework import viewsets, permissions
from .models import ReportDefinition, GeneratedReport, ReportSchedule
from .serializers import (
    ReportDefinitionSerializer, GeneratedReportSerializer, ReportScheduleSerializer
)


class ReportDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for ReportDefinition model."""
    queryset = ReportDefinition.objects.all()
    serializer_class = ReportDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ReportDefinition.objects.all()
        if hasattr(user, 'staff_profile'):
            return ReportDefinition.objects.filter(school=user.staff_profile.school)
        return ReportDefinition.objects.none()


class GeneratedReportViewSet(viewsets.ModelViewSet):
    """ViewSet for GeneratedReport model."""
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return GeneratedReport.objects.all()
        if hasattr(user, 'staff_profile'):
            return GeneratedReport.objects.filter(school=user.staff_profile.school)
        return GeneratedReport.objects.none()


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for ReportSchedule model."""
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ReportSchedule.objects.all()
        if hasattr(user, 'staff_profile'):
            return ReportSchedule.objects.filter(school=user.staff_profile.school)
        return ReportSchedule.objects.none()
