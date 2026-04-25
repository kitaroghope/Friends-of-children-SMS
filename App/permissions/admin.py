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
    readonly_fields = ['code', 'category']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['school', 'name', 'description', 'is_active', 'created_at']
    list_filter = ['school', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    actions = ['activate_roles', 'deactivate_roles']

    def activate_roles(self, request, queryset):
        """Activate selected roles."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} role(s) activated.')

    activate_roles.short_description = 'Activate Selected Roles'

    def deactivate_roles(self, request, queryset):
        """Deactivate selected roles."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} role(s) deactivated.')

    deactivate_roles.short_description = 'Deactivate Selected Roles'


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'granted_at', 'granted_by']
    list_filter = ['role', 'permission']
    search_fields = ['role__name', 'permission__name']
    raw_id_fields = ['role', 'permission']


@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ['staff', 'role', 'is_active', 'granted_at', 'expires_at', 'granted_by']
    list_filter = ['role', 'is_active']
    search_fields = ['staff__first_name', 'staff__last_name', 'role__name']
    raw_id_fields = ['staff', 'role', 'granted_by']
    readonly_fields = ['granted_at', 'granted_by']

    actions = ['activate_roles', 'deactivate_roles', 'revoke_roles']

    def activate_roles(self, request, queryset):
        """Activate selected staff roles."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} staff role(s) activated.')

    activate_roles.short_description = 'Activate Selected Staff Roles'

    def deactivate_roles(self, request, queryset):
        """Deactivate selected staff roles."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} staff role(s) deactivated.')

    deactivate_roles.short_description = 'Deactivate Selected Staff Roles'

    def revoke_roles(self, request, queryset):
        """Revoke (delete) selected staff roles."""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} staff role(s) revoked.')

    revoke_roles.short_description = 'Revoke Selected Staff Roles'
