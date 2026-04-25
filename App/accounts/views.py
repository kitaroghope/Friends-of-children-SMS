"""
Views for Accounts app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
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


class CurrentUserView(APIView):
    """Get the currently authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Return the current user's data."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


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
        """Initialize school academic structure from wizard data."""
        import sys

        print("="*50, file=sys.stderr)
        print("SchoolSetupView.create() called", file=sys.stderr)
        print(f"Method: {request.method}", file=sys.stderr)
        print(f"Content-Type: {request.content_type}", file=sys.stderr)
        print(f"Data received: {request.data}", file=sys.stderr)
        print("="*50, file=sys.stderr)

        user = request.user
        print(f"User: {user}", file=sys.stderr)

        try:
            staff_profile = user.staff_profile
            school = staff_profile.school
        except StaffProfile.DoesNotExist:
            print("ERROR: Staff profile not found", file=sys.stderr)
            return Response(
                {'error': 'Staff profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not staff_profile.is_active:
            print("ERROR: Account not active", file=sys.stderr)
            return Response(
                {'error': 'Your account is not active'},
                status=status.HTTP_403_FORBIDDEN
            )

        print(f"School: {school}", file=sys.stderr)

        # Check if already initialized
        if AcademicYear.objects.filter(school=school).exists():
            print("ERROR: School already initialized", file=sys.stderr)
            return Response(
                {'error': 'School already initialized'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data
        print(f"Full data: {data}", file=sys.stderr)

        year_data = data.get('year', {})
        terms_data = data.get('terms', [])
        sections_data = data.get('sections', [])
        classes_data = data.get('classes', {})
        subjects_data = data.get('subjects', [])

        print(f"year_data: {year_data}", file=sys.stderr)
        print(f"terms_data: {terms_data}", file=sys.stderr)
        print(f"sections_data: {sections_data}", file=sys.stderr)
        print(f"classes_data: {classes_data}", file=sys.stderr)
        print(f"subjects_data: {subjects_data}", file=sys.stderr)

        from datetime import datetime, date

        # Parse date strings from wizard
        def parse_date(date_str, field_name='field'):
            if date_str is None:
                raise ValueError(f"{field_name} is required")
            if isinstance(date_str, str):
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(f"Invalid date format for {field_name}: {date_str}")
            return date_str

        try:
            with transaction.atomic():
                # Create Academic Year
                year_value = year_data.get('name', str(timezone.now().year))
                try:
                    year_value = int(year_value)
                except (ValueError, TypeError):
                    year_value = timezone.now().year

                print(f"Creating AcademicYear with year={year_value}", file=sys.stderr)

                academic_year = AcademicYear.objects.create(
                    school=school,
                    year=year_value,
                    start_date=parse_date(year_data.get('start'), 'Academic year start date'),
                    end_date=parse_date(year_data.get('end'), 'Academic year end date'),
                    is_current=True
                )

                # Create Terms from wizard data
                terms_created = 0
                for i, term in enumerate(terms_data, 1):
                    Term.objects.create(
                        academic_year=academic_year,
                        term_number=i,
                        name=term.get('name', f'Term {i}'),
                        start_date=parse_date(term.get('start'), f'Term {i} start date'),
                        end_date=parse_date(term.get('end'), f'Term {i} end date'),
                        is_active=(i == 1)
                    )
                    terms_created += 1

                # Create Sections and Classes
                sections_created = 0
                classes_created = 0
                section_order = {'pre-primary': 1, 'primary': 2, 'secondary': 3}

                for section_key in sections_data:
                    section = Section.objects.create(
                        school=school,
                        name=section_key.replace('-', ' ').title(),
                        order=section_order.get(section_key, 99)
                    )
                    sections_created += 1

                    # Create Classes for this section
                    section_classes = classes_data.get(section_key, [])
                    for class_name in section_classes:
                        from academic.models import Class
                        Class.objects.create(
                            school=school,
                            section=section,
                            name=class_name
                        )
                        classes_created += 1

                # Create Subjects
                from academic.models import Subject
                subjects_created = 0
                for subject_name in subjects_data:
                    Subject.objects.create(
                        school=school,
                        name=subject_name,
                        code=subject_name[:3].upper()
                    )
                    subjects_created += 1

                # Create Default Grade Scale for Primary section
                primary_section = Section.objects.filter(school=school, name='Primary').first()
                if primary_section:
                    grade_scale = GradeScale.objects.create(
                        school=school,
                        section=primary_section,
                        name='Primary Grading (D1-F9)',
                        is_default=True
                    )
                    for grade in PRIMARY_GRADES:
                        GradeLevel.objects.create(
                            grade_scale=grade_scale,
                            **grade
                        )

            print("School setup completed successfully!", file=sys.stderr)
            return Response({
                'message': 'School initialized successfully',
                'academic_year': academic_year.id,
                'terms_created': terms_created,
                'sections_created': sections_created,
                'classes_created': classes_created,
                'subjects_created': subjects_created,
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            print(f"ValueError: {e}", file=sys.stderr)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Exception: {e}", file=sys.stderr)
            return Response(
                {'error': f'Setup failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
