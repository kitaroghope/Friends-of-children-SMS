"""
URL configuration for Reports app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ReportDefinitionViewSet, GeneratedReportViewSet, ReportScheduleViewSet,
    ReportSummaryView, EnrollmentReportView, AttendanceReportView,
    FinancialReportView, ExamReportView, StudentReportView
)

router = DefaultRouter()
router.register(r'definitions', ReportDefinitionViewSet, basename='reports-definition')
router.register(r'generated', GeneratedReportViewSet, basename='reports-generated')
router.register(r'schedules', ReportScheduleViewSet, basename='reports-schedule')

urlpatterns = router.urls + [
    path('summary/', ReportSummaryView.as_view(), name='reports-summary'),
    path('enrollment/', EnrollmentReportView.as_view(), name='reports-enrollment'),
    path('attendance/', AttendanceReportView.as_view(), name='reports-attendance'),
    path('financial/', FinancialReportView.as_view(), name='reports-financial'),
    path('exams/', ExamReportView.as_view(), name='reports-exams'),
    path('student/', StudentReportView.as_view(), name='reports-student'),
]
