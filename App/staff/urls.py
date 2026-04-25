"""
URL configuration for Staff app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import StaffProfileViewSet, my_profile_view

router = DefaultRouter()
router.register(r'staff', StaffProfileViewSet, basename='staff-staff')

urlpatterns = router.urls + [
    path('profile/', my_profile_view, name='my_profile'),
]
