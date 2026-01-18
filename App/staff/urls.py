"""
URL configuration for Staff app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import StaffProfileViewSet

router = DefaultRouter()
router.register(r'staff', StaffProfileViewSet, basename='staff-staff')

urlpatterns = router.urls
