"""
Admin configuration for Accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    list_display = ['email', 'first_name', 'last_name', 'user_type', 'is_active', 'last_login']
    list_filter = ['user_type', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Type', {'fields': ('user_type',)}),
        ('Status', {'fields': ('is_active',)}),
        ('Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ['last_login', 'created_at', 'updated_at']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type'),
        }),
    )
