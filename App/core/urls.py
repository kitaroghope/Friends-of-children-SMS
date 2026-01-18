"""
API URLs for Core app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet, AuditLogViewSet

router = DefaultRouter()
router.register(r'schools', SchoolViewSet, basename='core-school')
router.register(r'audit-logs', AuditLogViewSet, basename='core-audit')

urlpatterns = router.urls
