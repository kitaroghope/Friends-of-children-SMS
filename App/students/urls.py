"""
URL configuration for Students app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='students-student')
router.register(r'enrollments', EnrollmentViewSet, basename='students-enrollment')

urlpatterns = router.urls
