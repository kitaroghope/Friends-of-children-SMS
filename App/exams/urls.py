"""
URL configuration for Exams app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import GradeScaleViewSet, ExamSetViewSet, ExamViewSet, ResultViewSet

router = DefaultRouter()
router.register(r'grade-scales', GradeScaleViewSet, basename='exams-grade-scale')
router.register(r'exam-sets', ExamSetViewSet, basename='exams-exam-set')
router.register(r'exams', ExamViewSet, basename='exams-exam')
router.register(r'results', ResultViewSet, basename='exams-result')

urlpatterns = router.urls
