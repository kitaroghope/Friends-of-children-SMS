"""
Views for Staff app.
"""

from rest_framework import viewsets, permissions
from .models import StaffProfile
from .serializers import StaffProfileSerializer


class StaffProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for StaffProfile model."""
    queryset = StaffProfile.objects.all()
    serializer_class = StaffProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return StaffProfile.objects.all()
        if hasattr(user, 'staff_profile'):
            return StaffProfile.objects.filter(school=user.staff_profile.school)
        return StaffProfile.objects.none()
