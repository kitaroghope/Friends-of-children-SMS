"""
Views for Exams app.
"""

from rest_framework import viewsets, permissions
from .models import GradeScale, ExamSet, Exam, Result
from .serializers import GradeScaleSerializer, ExamSetSerializer, ExamSerializer, ResultSerializer


class GradeScaleViewSet(viewsets.ModelViewSet):
    """ViewSet for GradeScale model."""
    queryset = GradeScale.objects.all()
    serializer_class = GradeScaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return GradeScale.objects.all()
        if hasattr(user, 'staff_profile'):
            return GradeScale.objects.filter(school=user.staff_profile.school)
        return GradeScale.objects.none()


class ExamSetViewSet(viewsets.ModelViewSet):
    """ViewSet for ExamSet model."""
    queryset = ExamSet.objects.all()
    serializer_class = ExamSetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ExamSet.objects.all()
        if hasattr(user, 'staff_profile'):
            return ExamSet.objects.filter(school=user.staff_profile.school)
        return ExamSet.objects.none()


class ExamViewSet(viewsets.ModelViewSet):
    """ViewSet for Exam model."""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Exam.objects.all()
        if hasattr(user, 'staff_profile'):
            return Exam.objects.filter(school=user.staff_profile.school)
        return Exam.objects.none()


class ResultViewSet(viewsets.ModelViewSet):
    """ViewSet for Result model."""
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Result.objects.all()
        if hasattr(user, 'staff_profile'):
            return Result.objects.filter(school=user.staff_profile.school)
        return Result.objects.none()
