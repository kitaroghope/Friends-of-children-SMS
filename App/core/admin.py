"""
Admin configuration for Core app.
"""

from django.contrib import admin
from .models import School, AuditLog, SequenceNumber, Config, SchoolRequest


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'acronym', 'currency', 'is_active', 'created_at']
    list_filter = ['is_active', 'currency']
    search_fields = ['name', 'acronym', 'email']
    ordering = ['name']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'action', 'model_name', 'timestamp', 'is_offline']
    list_filter = ['action', 'is_offline', 'timestamp']
    search_fields = ['model_name', 'object_id']
    readonly_fields = ['user', 'school', 'action', 'model_name', 'object_id',
                       'old_values', 'new_values', 'ip_address', 'user_agent',
                       'timestamp', 'is_offline', 'sync_batch_id']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'


@admin.register(SequenceNumber)
class SequenceNumberAdmin(admin.ModelAdmin):
    list_display = ['school', 'prefix', 'year', 'model_name', 'sequence']
    list_filter = ['school', 'model_name', 'year']
    readonly_fields = ['sequence']


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['school', 'pass_mark_default', 'promotion_rule_type',
                    'require_all_compulsory_for_promotion', 'auto_approve_results']
    fieldsets = (
        (None, {'fields': ('school',)}),
        ('Promotion Settings', {'fields': (
            'pass_mark_default', 'promotion_rule_type',
            'require_all_compulsory_for_promotion', 'allow_manual_promotion_override'
        )}),
        ('Result Settings', {'fields': ('auto_approve_results',)}),
        ('Finance Settings', {'fields': (
            'invoice_group_by_parent', 'allow_overpayment', 'require_refund_approval'
        )}),
    )


@admin.register(SchoolRequest)
class SchoolRequestAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'requester_name', 'requester_email',
                    'status', 'school', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['school_name', 'requester_name', 'requester_email']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_by', 'reviewed_at']
    ordering = ['-created_at']

    actions = ['approve_and_create_school', 'reject_requests']

    fieldsets = (
        ('Requester Information', {'fields': (
            'requester_name', 'requester_email', 'requester_phone'
        )}),
        ('School Information', {'fields': (
            'school_name', 'school_acronym', 'school_phone',
            'school_email', 'school_address', 'currency', 'notes'
        )}),
        ('Review', {'fields': ('status', 'school', 'reviewed_by', 'reviewed_at', 'rejection_reason')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def approve_and_create_school(self, request, queryset):
        """Approve requests and create schools with owners."""
        import secrets
        from django.utils import timezone
        from django.db import transaction
        from accounts.models import User
        from core.models import School, Config, AuditLog
        from staff.models import StaffProfile
        from permissions.models import Role, StaffRole

        created_schools = []
        errors = []

        def generate_password():
            """Generate a random 12-character password."""
            alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%'
            return ''.join(secrets.choice(alphabet) for _ in range(12))

        for school_request in queryset.filter(status='pending'):
            try:
                with transaction.atomic():
                    temp_password = generate_password()

                    # Check if user already exists
                    user, created = User.objects.get_or_create(
                        email=school_request.requester_email,
                        defaults={
                            'first_name': school_request.requester_name.split()[0] if school_request.requester_name else 'Admin',
                            'last_name': ' '.join(school_request.requester_name.split()[1:]) if school_request.requester_name else 'Owner',
                            'user_type': 'staff'
                        }
                    )
                    if created:
                        user.set_password(temp_password)
                        user.save()
                    else:
                        # Update password for existing user
                        temp_password = '(existing user - password unchanged)'
                        user.first_name = school_request.requester_name.split()[0] if school_request.requester_name else user.first_name
                        user.last_name = ' '.join(school_request.requester_name.split()[1:]) if school_request.requester_name else user.last_name
                        user.user_type = 'staff'
                        user.save()

                    # Check if school already exists for this request
                    if school_request.school:
                        self.message_user(
                            request,
                            f"School for '{school_request.school_name}' already exists. Skipping.",
                            level='warning'
                        )
                        continue

                    # 2. Create School
                    school = School.objects.create(
                        name=school_request.school_name,
                        acronym=school_request.school_acronym.upper(),
                        phone=school_request.school_phone,
                        email=school_request.school_email,
                        address=school_request.school_address,
                        currency=school_request.currency,
                        is_active=True,
                    )

                    # 3. Create default Config
                    Config.objects.create(school=school)

                    # 4. Create StaffProfile for the owner (or get existing)
                    staff, staff_created = StaffProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'school': school,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'phone': school_request.requester_phone or '',
                            'email': user.email,
                            'position': 'School Owner',
                            'department': 'Administration',
                            'status': 'active'
                        }
                    )
                    if not staff_created:
                        staff.school = school
                        staff.status = 'active'
                        staff.save()

                    # 5. Create Admin Role and assign to owner
                    admin_role, role_created = Role.objects.get_or_create(
                        school=school,
                        defaults={
                            'name': 'School Administrator',
                            'description': 'Full school access - can manage all aspects of the school'
                        }
                    )
                    # Assign role if not already assigned
                    if not StaffRole.objects.filter(staff=staff, role=admin_role).exists():
                        StaffRole.objects.create(
                            staff=staff,
                            role=admin_role
                        )

                    # 6. Update request status
                    school_request.status = 'approved'
                    school_request.reviewed_by = request.user
                    school_request.reviewed_at = timezone.now()
                    school_request.school = school
                    school_request.save()

                    # 7. Create audit log
                    AuditLog.objects.create(
                        user=request.user,
                        school=school,
                        action='approve',
                        model_name='SchoolRequest',
                        object_id=str(school_request.id),
                        new_values={'school_id': school.id, 'status': 'approved'}
                    )

                    created_schools.append({
                        'name': school_request.school_name,
                        'email': school_request.requester_email,
                        'password': temp_password
                    })

            except Exception as e:
                import traceback
                traceback.print_exc()
                errors.append(f"{school_request.school_name}: {str(e)}")

        if created_schools:
            for school in created_schools:
                self.message_user(
                    request,
                    f"School '{school['name']}' created. Owner: {school['email']} | Password: {school['password']}",
                    level='success'
                )
        if errors:
            self.message_user(request, f'Errors: {"; ".join(errors)}', level='ERROR')

    approve_and_create_school.short_description = 'Approve & Create School'

    def reject_requests(self, request, queryset):
        """Reject selected school requests."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} request(s) rejected.')
    reject_requests.short_description = 'Reject selected requests'
