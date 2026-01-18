"""
Views for Parents app.
"""

from rest_framework import viewsets, permissions
from .models import ParentProfile, StudentParent
from .serializers import ParentProfileSerializer, StudentParentSerializer


class ParentProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for ParentProfile model."""
    queryset = ParentProfile.objects.all()
    serializer_class = ParentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ParentProfile.objects.all()
        if hasattr(user, 'parent_profile'):
            return ParentProfile.objects.filter(school=user.parent_profile.school)
        if hasattr(user, 'staff_profile'):
            return ParentProfile.objects.filter(school=user.staff_profile.school)
        return ParentProfile.objects.none()


class StudentParentViewSet(viewsets.ModelViewSet):
    """ViewSet for StudentParent model."""
    queryset = StudentParent.objects.all()
    serializer_class = StudentParentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return StudentParent.objects.all()
        if hasattr(user, 'staff_profile'):
            return StudentParent.objects.filter(school=user.staff_profile.school)
        return StudentParent.objects.none()
