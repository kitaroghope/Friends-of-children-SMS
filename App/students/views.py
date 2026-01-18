"""
Views for Students app.
"""

from rest_framework import viewsets, permissions
from .models import Student, Enrollment
from .serializers import StudentSerializer, EnrollmentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    """ViewSet for Student model."""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Student.objects.all()
        if hasattr(user, 'staff_profile'):
            return Student.objects.filter(school=user.staff_profile.school)
        return Student.objects.none()


class EnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Enrollment model."""
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Enrollment.objects.all()
        if hasattr(user, 'staff_profile'):
            return Enrollment.objects.filter(school=user.staff_profile.school)
        return Enrollment.objects.none()
