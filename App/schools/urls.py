"""
URL configuration for Schools app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AcademicYearViewSet, TermViewSet, SectionViewSet

router = DefaultRouter()
router.register(r'academic-years', AcademicYearViewSet, basename='schools-academic-year')
router.register(r'terms', TermViewSet, basename='schools-term')
router.register(r'sections', SectionViewSet, basename='schools-section')

urlpatterns = router.urls
