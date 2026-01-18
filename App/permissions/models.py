"""
Permission and Role models for the SMS system.
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models import BaseModel, School


class Permission(BaseModel):
    """
    Atomic permission that can be assigned to roles.
    Permissions are categorized and reusable across schools.
    """
    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('finance', 'Finance'),
        ('admin', 'Admin'),
    ]

    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    class Meta:
        ordering = ['category', 'code']

    def __str__(self):
        return f"{self.code} ({self.category})"


class Role(BaseModel):
    """
    Role that groups permissions together.
    Roles are school-specific to allow different permission sets per school.
    """
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['school', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.school.acronym} - {self.name}"

    def has_permission(self, permission_code):
        """Check if role has a specific permission."""
        return self.permissions.filter(code=permission_code).exists()

    def get_all_permissions(self):
        """Return all permission codes for this role."""
        return list(self.permissions.values_list('code', flat=True))


class RolePermission(BaseModel):
    """
    Many-to-many relationship between roles and permissions.
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ['role', 'permission']

    def __str__(self):
        return f"{self.role.name} -> {self.permission.code}"


class StaffRole(BaseModel):
    """
    Many-to-many relationship between staff profiles and roles.
    """
    staff = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.CASCADE,
        related_name='staff_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='staff_roles'
    )
    is_active = models.BooleanField(default=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles_granted'
    )
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['staff', 'role']

    def __str__(self):
        return f"{self.staff} has {self.role.name}"

    def is_expired(self):
        """Check if the role assignment has expired."""
        if self.expires_at:
            from django.utils import timezone
            return self.expires_at < timezone.now()
        return False
