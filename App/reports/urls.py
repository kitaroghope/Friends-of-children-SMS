"""
URL configuration for Reports app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ReportDefinitionViewSet, GeneratedReportViewSet, ReportScheduleViewSet

router = DefaultRouter()
router.register(r'definitions', ReportDefinitionViewSet, basename='reports-definition')
router.register(r'generated', GeneratedReportViewSet, basename='reports-generated')
router.register(r'schedules', ReportScheduleViewSet, basename='reports-schedule')

urlpatterns = router.urls
