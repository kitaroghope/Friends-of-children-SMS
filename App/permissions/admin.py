"""
Admin configuration for Permissions app.
"""

from django.contrib import admin
from .models import Permission, Role, RolePermission, StaffRole


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'description']
    list_filter = ['category']
    search_fields = ['code', 'name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['school', 'name', 'description', 'is_active']
    list_filter = ['school', 'is_active']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'granted_at', 'granted_by']
    list_filter = ['role', 'permission']


@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ['staff', 'role', 'is_active', 'granted_at', 'expires_at']
    list_filter = ['school', 'role', 'is_active']
