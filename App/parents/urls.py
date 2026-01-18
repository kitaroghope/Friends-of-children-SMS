"""
URL configuration for Parents app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ParentProfileViewSet, StudentParentViewSet

router = DefaultRouter()
router.register(r'parents', ParentProfileViewSet, basename='parents-parent')
router.register(r'student-parents', StudentParentViewSet, basename='parents-student-parent')

urlpatterns = router.urls
