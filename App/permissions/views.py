"""
Views for Permissions app.
"""

from rest_framework import viewsets, permissions
from .models import Permission, Role, StaffRole
from .serializers import PermissionSerializer, RoleSerializer, StaffRoleSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for Permission model."""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for Role model."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Role.objects.all()
        if hasattr(user, 'staff_profile'):
            return Role.objects.filter(school=user.staff_profile.school)
        return Role.objects.none()


class StaffRoleViewSet(viewsets.ModelViewSet):
    """ViewSet for StaffRole model."""
    queryset = StaffRole.objects.all()
    serializer_class = StaffRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return StaffRole.objects.all()
        if hasattr(user, 'staff_profile'):
            return StaffRole.objects.filter(school=user.staff_profile.school)
        return StaffRole.objects.none()
