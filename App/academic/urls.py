"""
URL configuration for Academic app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ClassViewSet, SubjectViewSet, ClassSubjectViewSet, TeachingAssignmentViewSet

router = DefaultRouter()
router.register(r'classes', ClassViewSet, basename='academic-class')
router.register(r'subjects', SubjectViewSet, basename='academic-subject')
router.register(r'class-subjects', ClassSubjectViewSet, basename='academic-class-subject')
router.register(r'teaching-assignments', TeachingAssignmentViewSet, basename='academic-teaching')

urlpatterns = router.urls
