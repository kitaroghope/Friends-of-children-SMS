"""
Admin configuration for Staff app.
"""

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from .models import StaffProfile, StaffStatusHistory


class AssignRoleForm:
    """Simple form for role assignment."""
    def __init__(self, roles, staff_members, *args, **kwargs):
        self.roles = roles
        self.staff_members = staff_members


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['staff_number', 'first_name', 'last_name', 'school', 'status', 'date_joined']
    list_filter = ['school', 'status', 'department']
    search_fields = ['staff_number', 'first_name', 'last_name', 'email']
    ordering = ['school', 'last_name', 'first_name']
    readonly_fields = ['date_joined', 'created_at', 'updated_at']

    actions = ['assign_role']

    def assign_role(self, request, queryset):
        """Assign a role to selected staff members."""
        from permissions.models import Role, StaffRole

        # Get the school from selected staff
        school = queryset.first().school if queryset else None
        if not school:
            self.message_user(request, 'Please select staff members from the same school.', level='ERROR')
            return HttpResponseRedirect(request.get_full_path())

        # Get available roles for this school
        roles = Role.objects.filter(school=school, is_active=True)

        if not roles.exists():
            self.message_user(request, 'No roles available for this school. Create roles first in Permissions > Roles.', level='ERROR')
            return HttpResponseRedirect(request.get_full_path())

        if request.POST.get('post'):
            role_id = request.POST.get('role_id')
            if role_id:
                role = Role.objects.get(id=role_id)
                assigned = 0
                for staff in queryset:
                    if not StaffRole.objects.filter(staff=staff, role=role).exists():
                        StaffRole.objects.create(
                            staff=staff,
                            role=role,
                            granted_by=request.user
                        )
                        assigned += 1
                self.message_user(request, f'{assigned} staff member(s) assigned role: {role.name}')
            return HttpResponseRedirect(request.get_full_path())

        # Show confirmation page
        context = {
            'title': 'Assign Role',
            'staff_members': queryset,
            'roles': roles,
            'opts': self.model._meta,
            'action': 'assign_role',
        }
        return TemplateResponse(request, 'admin/staff/assign_role.html', context)

    assign_role.short_description = 'Assign Role to Selected Staff'


@admin.register(StaffStatusHistory)
class StaffStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['staff', 'old_status', 'new_status', 'effective_date', 'changed_by']
    list_filter = ['old_status', 'new_status']
    readonly_fields = ['staff', 'old_status', 'new_status', 'effective_date', 'changed_by']
