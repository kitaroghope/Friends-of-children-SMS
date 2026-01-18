"""
Views for Accounts app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from .models import User
from .serializers import (
    UserSerializer, UserRegistrationSerializer, SchoolRequestSerializer,
    SchoolOnboardingSerializer, StaffOnboardingSerializer,
    ParentOnboardingSerializer
)
from core.models import School, SchoolRequest, Config, AuditLog
from schools.models import AcademicYear, Term, Section
from exams.models import GradeScale, GradeLevel
from staff.models import StaffProfile
from parents.models import ParentProfile
from permissions.models import Role, StaffRole


# Primary grading scale defaults
PRIMARY_GRADES = [
    {'grade': 'D1', 'min_score': 80, 'max_score': 100, 'description': 'Distinction 1'},
    {'grade': 'D2', 'min_score': 75, 'max_score': 79, 'description': 'Distinction 2'},
    {'grade': 'C3', 'min_score': 70, 'max_score': 74, 'description': 'Credit 3'},
    {'grade': 'C4', 'min_score': 65, 'max_score': 69, 'description': 'Credit 4'},
    {'grade': 'C5', 'min_score': 60, 'max_score': 64, 'description': 'Credit 5'},
    {'grade': 'C6', 'min_score': 55, 'max_score': 59, 'description': 'Credit 6'},
    {'grade': 'P7', 'min_score': 50, 'max_score': 54, 'description': 'Pass 7'},
    {'grade': 'P8', 'min_score': 45, 'max_score': 49, 'description': 'Pass 8'},
    {'grade': 'F9', 'min_score': 0, 'max_score': 44, 'description': 'Fail'},
]


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter users based on staff/parent profiles."""
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(pk=user.pk)


class RegisterView(viewsets.ViewSet):
    """Public endpoint for user registration."""
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class SchoolRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for school registration requests.
    - POST: Anyone can submit a request
    - GET: Superadmin can list all requests
    - PUT: Superadmin can approve/reject
    """
    queryset = SchoolRequest.objects.all()
    serializer_class = SchoolRequestSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Filter based on user role."""
        user = self.request.user
        if user.is_authenticated and user.is_superuser:
            return SchoolRequest.objects.all()
        return SchoolRequest.objects.none()

    def create(self, request):
        """Submit a new school registration request."""
        serializer = SchoolRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        school_request = serializer.save()
        return Response(
            SchoolRequestSerializer(school_request).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        """Approve or reject a school request (superadmin only)."""
        user = request.user
        if not user.is_authenticated or not user.is_superuser:
            return Response(
                {'error': 'Superadmin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            school_request = SchoolRequest.objects.get(pk=pk)
        except SchoolRequest.DoesNotExist:
            return Response(
                {'error': 'Request not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get('status')
        if new_status not in ['approved', 'rejected']:
            return Response(
                {'error': 'Status must be approved or rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        school_request.status = new_status
        school_request.reviewed_by = user
        school_request.reviewed_at = timezone.now()

        if new_status == 'rejected':
            school_request.rejection_reason = request.data.get(
                'rejection_reason', ''
            )

        school_request.save()

        # Log the action
        AuditLog.objects.create(
            user=user,
            action='approve' if new_status == 'approved' else 'reject',
            model_name='SchoolRequest',
            object_id=str(school_request.id),
            new_values={'status': new_status}
        )

        return Response(SchoolRequestSerializer(school_request).data)


class SchoolOnboardingView(viewsets.ViewSet):
    """
    Create a school with owner from an approved request.
    Superadmin only.
    """
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        """Onboard a new school from an approved request."""
        user = request.user
        if not user.is_superuser:
            return Response(
                {'error': 'Superadmin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SchoolOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        school_request = SchoolRequest.objects.get(
            id=serializer.validated_data['request_id'],
            status='approved'
        )

        with transaction.atomic():
            # 1. Create User (school owner)
            user = User.objects.create_user(
                email=school_request.requester_email,
                password=User.objects.make_random_password(),
                first_name=school_request.requester_name.split()[0],
                last_name=' '.join(school_request.requester_name.split()[1:]),
                phone=school_request.requester_phone,
                user_type='staff'
            )

            # 2. Create School
            school = School.objects.create(
                name=school_request.school_name,
                acronym=school_request.school_acronym.upper(),
                phone=school_request.school_phone,
                email=school_request.school_email,
                address=school_request.school_address,
                currency=school_request.currency
            )

            # 3. Create School Config
            Config.objects.create(school=school)

            # 4. Create StaffProfile as School Owner
            staff = StaffProfile.objects.create(
                user=user,
                school=school,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                email=user.email,
                position='School Owner',
                department='Administration',
                status='active'
            )

            # 5. Create Admin Role and assign to owner
            admin_role = Role.objects.create(
                school=school,
                name='School Administrator',
                description='Full school access'
            )
            StaffRole.objects.create(
                staff_profile=staff,
                role=admin_role
            )

        return Response({
            'message': 'School created successfully',
            'school': {
                'id': school.id,
                'name': school.name,
                'acronym': school.acronym,
            },
            'owner': {
                'id': user.id,
                'email': user.email,
            }
        }, status=status.HTTP_201_CREATED)


class StaffOnboardingView(viewsets.ViewSet):
    """Onboard new staff members (admin only)."""
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        """Add a new staff member to the current school."""
        user = request.user

        # Get user's staff profile and school
        try:
            staff_profile = user.staff_profile
            school = staff_profile.school
        except StaffProfile.DoesNotExist:
            return Response(
                {'error': 'Staff profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user can manage staff
        if not staff_profile.is_active:
            return Response(
                {'error': 'Your account is not active'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = StaffOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Create User
            new_user = User.objects.create_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                phone=serializer.validated_data['phone'],
                user_type='staff'
            )

            # Create StaffProfile
            staff = StaffProfile.objects.create(
                user=new_user,
                school=school,
                staff_number=serializer.validated_data['staff_number'],
                first_name=new_user.first_name,
                last_name=new_user.last_name,
                gender=serializer.validated_data['gender'],
                date_of_birth=serializer.validated_data['date_of_birth'],
                phone=new_user.phone,
                email=new_user.email,
                department=serializer.validated_data['department'],
                position=serializer.validated_data['position'],
                status='active'
            )

            # Assign roles
            role_codes = serializer.validated_data.get('role_codes', [])
            for code in role_codes:
                try:
                    role = Role.objects.get(school=school, code=code)
                    StaffRole.objects.create(staff_profile=staff, role=role)
                except Role.DoesNotExist:
                    pass

        return Response({
            'message': 'Staff member onboarded successfully',
            'staff': {
                'id': staff.id,
                'email': new_user.email,
                'staff_number': staff.staff_number,
            }
        }, status=status.HTTP_201_CREATED)


class ParentOnboardingView(viewsets.ViewSet):
    """Onboard parents (staff only)."""
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        """Add a parent to the current school."""
        user = request.user

        # Get user's school
        try:
            staff_profile = user.staff_profile
            school = staff_profile.school
        except StaffProfile.DoesNotExist:
            return Response(
                {'error': 'Staff profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not staff_profile.is_active:
            return Response(
                {'error': 'Your account is not active'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ParentOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Check if phone already exists in this school
        if ParentProfile.objects.filter(
            school=school, phone=data['phone']
        ).exists():
            return Response(
                {'error': 'A parent with this phone already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create user
        user_kwargs = {
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'user_type': 'parent'
        }
        if data.get('email'):
            user_kwargs['email'] = data['email']

        if data.get('password'):
            user, created = User.objects.get_or_create(
                phone=data['phone'],
                defaults=user_kwargs
            )
            if created:
                user.set_password(data['password'])
                user.save()
        else:
            user, created = User.objects.get_or_create(
                phone=data['phone'],
                defaults=user_kwargs
            )

        # Create ParentProfile
        profile = ParentProfile.objects.create(
            user=user,
            school=school,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email=data.get('email', ''),
            relationship=data['relationship']
        )

        return Response({
            'message': 'Parent onboarded successfully',
            'parent': {
                'id': profile.id,
                'name': f'{profile.first_name} {profile.last_name}',
                'phone': profile.phone,
            }
        }, status=status.HTTP_201_CREATED)


class SchoolSetupView(viewsets.ViewSet):
    """Manage initial school setup."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get setup status for the current school."""
        user = request.user

        try:
            staff_profile = user.staff_profile
            school = staff_profile.school
        except StaffProfile.DoesNotExist:
            return Response(
                {'error': 'Staff profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'has_academic_year': AcademicYear.objects.filter(school=school).exists(),
            'has_sections': Section.objects.filter(school=school).exists(),
            'has_classes': school.classes_set.exists(),
            'has_subjects': school.subjects_set.exists(),
            'has_grade_scales': GradeScale.objects.filter(school=school).exists(),
        })

    def create(self, request):
        """Initialize school academic structure."""
        user = request.user

        try:
            staff_profile = user.staff_profile
            school = staff_profile.school
        except StaffProfile.DoesNotExist:
            return Response(
                {'error': 'Staff profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not staff_profile.is_active:
            return Response(
                {'error': 'Your account is not active'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if already initialized
        if AcademicYear.objects.filter(school=school).exists():
            return Response(
                {'error': 'School already initialized'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from datetime import date
        current_year = timezone.now().year

        with transaction.atomic():
            # Create Academic Year
            academic_year = AcademicYear.objects.create(
                school=school,
                year=current_year,
                start_date=date(current_year, 1, 1),
                end_date=date(current_year, 12, 31),
                is_current=True
            )

            # Create 3 Terms
            term_dates = [
                (date(current_year, 1, 1), date(current_year, 4, 30)),
                (date(current_year, 5, 1), date(current_year, 8, 31)),
                (date(current_year, 9, 1), date(current_year, 12, 31)),
            ]
            for i, (start, end) in enumerate(term_dates, 1):
                Term.objects.create(
                    academic_year=academic_year,
                    term_number=i,
                    start_date=start,
                    end_date=end,
                    is_current=(i == 1)
                )

            # Create Sections
            primary_section = Section.objects.create(
                school=school, name='Primary', order=2
            )
            pre_primary = Section.objects.create(
                school=school, name='Pre-Primary', order=1
            )

            # Create Default Grade Scale for Primary
            grade_scale = GradeScale.objects.create(
                school=school,
                section=primary_section,
                name='Primary Grading',
                is_default=True
            )
            for grade in PRIMARY_GRADES:
                GradeLevel.objects.create(
                    grade_scale=grade_scale,
                    **grade
                )

        return Response({
            'message': 'School initialized successfully',
            'academic_year': academic_year.id,
            'terms_created': 3,
            'sections_created': 2,
        }, status=status.HTTP_201_CREATED)
