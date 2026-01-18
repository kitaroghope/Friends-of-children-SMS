"""
Views for Academic app.
"""

from rest_framework import viewsets, permissions
from .models import Class, Subject, ClassSubject, TeachingAssignment
from .serializers import (
    ClassSerializer, SubjectSerializer, ClassSubjectSerializer,
    TeachingAssignmentSerializer
)


class ClassViewSet(viewsets.ModelViewSet):
    """ViewSet for Class model."""
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Class.objects.all()
        if hasattr(user, 'staff_profile'):
            return Class.objects.filter(school=user.staff_profile.school)
        return Class.objects.none()


class SubjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Subject model."""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Subject.objects.all()
        if hasattr(user, 'staff_profile'):
            return Subject.objects.filter(school=user.staff_profile.school)
        return Subject.objects.none()


class ClassSubjectViewSet(viewsets.ModelViewSet):
    """ViewSet for ClassSubject model."""
    queryset = ClassSubject.objects.all()
    serializer_class = ClassSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ClassSubject.objects.all()
        if hasattr(user, 'staff_profile'):
            return ClassSubject.objects.filter(school=user.staff_profile.school)
        return ClassSubject.objects.none()


class TeachingAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for TeachingAssignment model."""
    queryset = TeachingAssignment.objects.all()
    serializer_class = TeachingAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return TeachingAssignment.objects.all()
        if hasattr(user, 'staff_profile'):
            return TeachingAssignment.objects.filter(school=user.staff_profile.school)
        return TeachingAssignment.objects.none()
