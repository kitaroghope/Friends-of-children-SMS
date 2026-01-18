"""
URL configuration for Accounts app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet, RegisterView, SchoolRequestViewSet, SchoolOnboardingView,
    StaffOnboardingView, ParentOnboardingView, SchoolSetupView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='accounts-user')
router.register(r'school-requests', SchoolRequestViewSet, basename='school-request')
router.register(r'onboarding/school', SchoolOnboardingView, basename='school-onboarding')
router.register(r'onboarding/staff', StaffOnboardingView, basename='staff-onboarding')
router.register(r'onboarding/parent', ParentOnboardingView, basename='parent-onboarding')
router.register(r'setup', SchoolSetupView, basename='school-setup')

urlpatterns = [
    path('register/', RegisterView.as_view({'post': 'create'}), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls
