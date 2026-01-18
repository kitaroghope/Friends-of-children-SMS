"""
Views for Schools app.
"""

from rest_framework import viewsets, permissions
from .models import AcademicYear, Term, Section
from .serializers import AcademicYearSerializer, TermSerializer, SectionSerializer


class AcademicYearViewSet(viewsets.ModelViewSet):
    """ViewSet for AcademicYear model."""
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return AcademicYear.objects.all()
        if hasattr(user, 'staff_profile'):
            return AcademicYear.objects.filter(school=user.staff_profile.school)
        return AcademicYear.objects.none()


class TermViewSet(viewsets.ModelViewSet):
    """ViewSet for Term model."""
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Term.objects.all()
        if hasattr(user, 'staff_profile'):
            return Term.objects.filter(academic_year__school=user.staff_profile.school)
        return Term.objects.none()


class SectionViewSet(viewsets.ModelViewSet):
    """ViewSet for Section model."""
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Section.objects.all()
        if hasattr(user, 'staff_profile'):
            return Section.objects.filter(school=user.staff_profile.school)
        return Section.objects.none()
