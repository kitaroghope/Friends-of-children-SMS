"""
URL configuration for Permissions app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PermissionViewSet, RoleViewSet, StaffRoleViewSet

router = DefaultRouter()
router.register(r'permissions', PermissionViewSet, basename='permissions-permission')
router.register(r'roles', RoleViewSet, basename='permissions-role')
router.register(r'staff-roles', StaffRoleViewSet, basename='permissions-staff-role')

urlpatterns = router.urls
