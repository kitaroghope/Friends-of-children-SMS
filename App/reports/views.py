"""
Views for Reports app.
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncMonth
from django.db import models as db_models
from datetime import datetime, timedelta
from .models import ReportDefinition, GeneratedReport, ReportSchedule
from .serializers import (
    ReportDefinitionSerializer, GeneratedReportSerializer, ReportScheduleSerializer
)


class ReportDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for ReportDefinition model."""
    queryset = ReportDefinition.objects.all()
    serializer_class = ReportDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ReportDefinition.objects.all()
        if hasattr(user, 'staff_profile'):
            return ReportDefinition.objects.filter(school=user.staff_profile.school)
        return ReportDefinition.objects.none()


class GeneratedReportViewSet(viewsets.ModelViewSet):
    """ViewSet for GeneratedReport model."""
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = GeneratedReport.objects.all()
        if user.is_superuser:
            return queryset
        if hasattr(user, 'staff_profile'):
            return queryset.filter(school=user.staff_profile.school)
        return GeneratedReport.objects.none()


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for ReportSchedule model."""
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ReportSchedule.objects.all()
        if hasattr(user, 'staff_profile'):
            return ReportSchedule.objects.filter(school=user.staff_profile.school)
        return ReportSchedule.objects.none()


class ReportSummaryView(APIView):
    """API endpoint for dashboard report summary data."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get summary statistics for dashboard."""
        user = request.user
        school = None

        if hasattr(user, 'staff_profile'):
            school = user.staff_profile.school
        elif user.is_superuser:
            pass  # Superuser sees all
        else:
            return Response({"error": "Access denied"}, status=403)

        # Import here to avoid circular imports
        from students.models import Student
        from finance.models import Invoice, Payment
        from academic.models import Class, Enrollment

        # Get current academic year and term if available
        from schools.models import AcademicYear, Term
        now = datetime.now()
        try:
            current_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).first()
            current_term = None
            if current_year:
                current_term = Term.objects.filter(
                    academic_year=current_year,
                    start_date__lte=now,
                    end_date__gte=now
                ).first()
        except:
            current_year = None
            current_term = None

        # Base filters
        school_filter = {'school': school} if school else {}
        year_filter = {'academic_year': current_year} if current_year else {}
        term_filter = {'term': current_term} if current_term else {}

        # Student statistics
        if school:
            total_students = Student.objects.filter(enrollments__school=school).distinct().count()
            active_students = Student.objects.filter(
                enrollments__school=school,
                enrollments__status='active'
            ).distinct().count()
        else:
            total_students = Student.objects.count()
            active_students = Student.objects.filter(enrollments__status='active').distinct().count()

        # Class statistics
        if school:
            total_classes = Class.objects.filter(school=school).count()
        else:
            total_classes = Class.objects.count()

        # Financial summary
        if school:
            total_invoiced = Invoice.objects.filter(**school_filter, **year_filter).aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            total_collected = Payment.objects.filter(**school_filter, **year_filter).aggregate(
                total=Sum('amount')
            )['total'] or 0
            outstanding = Invoice.objects.filter(
                **school_filter, **year_filter
            ).aggregate(balance=Sum('balance'))['balance'] or 0
        else:
            total_invoiced = Invoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0
            total_collected = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
            outstanding = Invoice.objects.aggregate(balance=Sum('balance'))['balance'] or 0

        # Monthly collection trend (last 6 months)
        monthly_trend = []
        for i in range(5, -1, -1):
            month_start = now.replace(day=1) - timedelta(days=i * 30)
            month_end = month_start.replace(day=28) + timedelta(days=4)
            if school:
                month_data = Payment.objects.filter(
                    **school_filter,
                    payment_date__gte=month_start,
                    payment_date__lte=month_end
                ).aggregate(total=Sum('amount'))['total'] or 0
            else:
                month_data = Payment.objects.filter(
                    payment_date__gte=month_start,
                    payment_date__lte=month_end
                ).aggregate(total=Sum('amount'))['total'] or 0
            monthly_trend.append({
                'month': month_start.strftime('%b %Y'),
                'amount': float(month_data)
            })

        return Response({
            'students': {
                'total': total_students,
                'active': active_students,
            },
            'classes': {
                'total': total_classes,
            },
            'financial': {
                'total_invoiced': float(total_invoiced),
                'total_collected': float(total_collected),
                'outstanding': float(outstanding),
                'collection_rate': round((float(total_collected) / float(total_invoiced) * 100), 1) if total_invoiced > 0 else 0,
            },
            'monthly_trend': monthly_trend,
            'current_year': current_year.name if current_year else None,
            'current_term': current_term.name if current_term else None,
        })


class EnrollmentReportView(APIView):
    """API endpoint for enrollment reports."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get enrollment statistics by class, section, etc."""
        user = request.user
        school = getattr(user, 'staff_profile', None).school if hasattr(user, 'staff_profile') else None

        from students.models import Student
        from academic.models import Class, Enrollment
        from schools.models import AcademicYear, Term

        now = datetime.now()
        try:
            current_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).first()
        except:
            current_year = None

        base_filters = {'school': school} if school else {}
        year_filter = {'academic_year': current_year} if current_year else {}

        # Enrollment by class
        if school:
            class_enrollment = Enrollment.objects.filter(
                **base_filters,
                status='active',
                **year_filter
            ).values('class_obj__name').annotate(
                count=Count('id')
            ).order_by('class_obj__name')
        else:
            class_enrollment = Enrollment.objects.filter(
                status='active',
                **year_filter
            ).values('class_obj__name').annotate(
                count=Count('id')
            ).order_by('class_obj__name')

        # Gender distribution
        if school:
            gender_dist = Enrollment.objects.filter(
                **base_filters,
                status='active',
                **year_filter
            ).values('student__gender').annotate(
                count=Count('id')
            )
        else:
            gender_dist = Enrollment.objects.filter(
                status='active',
                **year_filter
            ).values('student__gender').annotate(
                count=Count('id')
            )

        # Boarding vs day
        if school:
            boarding_dist = Enrollment.objects.filter(
                **base_filters,
                status='active',
                **year_filter
            ).values('boarding_status').annotate(
                count=Count('id')
            )
        else:
            boarding_dist = Enrollment.objects.filter(
                status='active',
                **year_filter
            ).values('boarding_status').annotate(
                count=Count('id')
            )

        return Response({
            'by_class': list(class_enrollment),
            'by_gender': list(gender_dist),
            'by_boarding': list(boarding_dist),
        })


class AttendanceReportView(APIView):
    """API endpoint for attendance reports."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get attendance statistics."""
        user = request.user
        school = getattr(user, 'staff_profile', None).school if hasattr(user, 'staff_profile') else None

        from attendance.models import AttendanceRecord, DailyAttendance
        from academic.models import Class
        from schools.models import AcademicYear, Term

        now = datetime.now()
        try:
            current_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).first()
            current_term = Term.objects.filter(
                academic_year=current_year,
                start_date__lte=now,
                end_date__gte=now
            ).first() if current_year else None
        except:
            current_year = None
            current_term = None

        base_filters = {'school': school} if school else {}
        year_filter = {'academic_year': current_year} if current_year else {}

        # Get attendance statistics
        if school:
            attendance_stats = DailyAttendance.objects.filter(
                **base_filters,
                **year_filter,
                date__month=now.month,
                date__year=now.year
            ).aggregate(
                total_students=Sum('total_students'),
                present=Sum('present'),
                absent=Sum('absent'),
                late=Sum('late')
            )
        else:
            attendance_stats = DailyAttendance.objects.filter(
                **year_filter,
                date__month=now.month,
                date__year=now.year
            ).aggregate(
                total_students=Sum('total_students'),
                present=Sum('present'),
                absent=Sum('absent'),
                late=Sum('late')
            )

        # Attendance by class (last 30 days)
        date_from = now - timedelta(days=30)
        if school:
            class_attendance = DailyAttendance.objects.filter(
                **base_filters,
                **year_filter,
                date__gte=date_from
            ).values('class_obj__name').annotate(
                avg_present=Avg('present'),
                avg_absent=Avg('absent')
            ).order_by('class_obj__name')[:10]
        else:
            class_attendance = DailyAttendance.objects.filter(
                **year_filter,
                date__gte=date_from
            ).values('class_obj__name').annotate(
                avg_present=Avg('present'),
                avg_absent=Avg('absent')
            ).order_by('class_obj__name')[:10]

        total = attendance_stats['total_students'] or 0
        present = attendance_stats['present'] or 0
        absent = attendance_stats['absent'] or 0
        late = attendance_stats['late'] or 0

        return Response({
            'monthly': {
                'total_students': total,
                'present': present,
                'absent': absent,
                'late': late,
                'attendance_rate': round((present / total * 100), 1) if total > 0 else 0,
            },
            'by_class': list(class_attendance),
        })


class FinancialReportView(APIView):
    """API endpoint for financial reports."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get financial statistics and fee collection."""
        user = request.user
        school = getattr(user, 'staff_profile', None).school if hasattr(user, 'staff_profile') else None

        from finance.models import Invoice, Payment, FeeStructure
        from schools.models import AcademicYear, Term

        now = datetime.now()
        try:
            current_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).first()
            current_term = Term.objects.filter(
                academic_year=current_year,
                start_date__lte=now,
                end_date__gte=now
            ).first() if current_year else None
        except:
            current_year = None
            current_term = None

        base_filters = {'school': school} if school else {}
        year_filter = {'academic_year': current_year} if current_year else {}
        term_filter = {'term': current_term} if current_term else {}

        # Fee collection summary
        if school:
            fee_summary = Invoice.objects.filter(
                **base_filters,
                **year_filter
            ).aggregate(
                total_invoiced=Sum('total_amount'),
                total_paid=Sum('amount_paid'),
                total_balance=Sum('balance')
            )
            payments = Payment.objects.filter(
                **base_filters,
                **year_filter
            ).values('payment_method').annotate(
                total=Sum('amount')
            ).order_by('-total')
        else:
            fee_summary = Invoice.objects.filter(**year_filter).aggregate(
                total_invoiced=Sum('total_amount'),
                total_paid=Sum('amount_paid'),
                total_balance=Sum('balance')
            )
            payments = Payment.objects.filter(**year_filter).values('payment_method').annotate(
                total=Sum('amount')
            ).order_by('-total')

        # Outstanding invoices by status
        if school:
            outstanding_by_status = Invoice.objects.filter(
                **base_filters,
                **year_filter,
                balance__gt=0
            ).values('status').annotate(
                count=Count('id'),
                total=Sum('balance')
            )
        else:
            outstanding_by_status = Invoice.objects.filter(
                **year_filter,
                balance__gt=0
            ).values('status').annotate(
                count=Count('id'),
                total=Sum('balance')
            )

        # Monthly collection (last 6 months)
        monthly_collection = []
        for i in range(5, -1, -1):
            month_start = now.replace(day=1) - timedelta(days=i * 30)
            month_end = month_start.replace(day=28) + timedelta(days=4)
            if school:
                month_data = Payment.objects.filter(
                    **base_filters,
                    payment_date__gte=month_start,
                    payment_date__lte=month_end
                ).aggregate(total=Sum('amount'))['total'] or 0
            else:
                month_data = Payment.objects.filter(
                    payment_date__gte=month_start,
                    payment_date__lte=month_end
                ).aggregate(total=Sum('amount'))['total'] or 0
            monthly_collection.append({
                'month': month_start.strftime('%b %Y'),
                'amount': float(month_data)
            })

        total_invoiced = fee_summary['total_invoiced'] or 0
        total_paid = fee_summary['total_paid'] or 0

        return Response({
            'summary': {
                'total_invoiced': float(total_invoiced),
                'total_paid': float(total_paid),
                'total_balance': float(fee_summary['total_balance'] or 0),
                'collection_rate': round((float(total_paid) / float(total_invoiced) * 100), 1) if total_invoiced > 0 else 0,
            },
            'by_payment_method': list(payments),
            'outstanding_by_status': list(outstanding_by_status),
            'monthly_collection': monthly_collection,
        })


class ExamReportView(APIView):
    """API endpoint for exam results reports."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get exam results statistics."""
        user = request.user
        school = getattr(user, 'staff_profile', None).school if hasattr(user, 'staff_profile') else None

        from exams.models import ExamResult, ExamSet
        from academic.models import Class
        from schools.models import AcademicYear, Term

        now = datetime.now()
        try:
            current_year = AcademicYear.objects.filter(start_date__lte=now, end_date__gte=now).first()
            current_term = Term.objects.filter(
                academic_year=current_year,
                start_date__lte=now,
                end_date__gte=now
            ).first() if current_year else None
        except:
            current_year = None
            current_term = None

        base_filters = {'school': school} if school else {}
        year_filter = {'exam_set__academic_year': current_year} if current_year else {}
        term_filter = {'exam_set__term': current_term} if current_term else {}

        # Grade distribution
        if school:
            grade_dist = ExamResult.objects.filter(
                **base_filters,
                **year_filter
            ).values('grade').annotate(
                count=Count('id')
            ).order_by('grade')
        else:
            grade_dist = ExamResult.objects.filter(**year_filter).values('grade').annotate(
                count=Count('id')
            ).order_by('grade')

        # Average score by class
        if school:
            class_performance = ExamResult.objects.filter(
                **base_filters,
                **year_filter
            ).values('student__current_class__name').annotate(
                avg_score=Avg('percentage'),
                count=Count('id')
            ).order_by('-avg_score')
        else:
            class_performance = ExamResult.objects.filter(**year_filter).values(
                'student__current_class__name'
            ).annotate(
                avg_score=Avg('percentage'),
                count=Count('id')
            ).order_by('-avg_score')

        # Subject performance
        if school:
            subject_performance = ExamResult.objects.filter(
                **base_filters,
                **year_filter
            ).values('subject__name').annotate(
                avg_score=Avg('percentage'),
                count=Count('id')
            ).order_by('-avg_score')[:10]
        else:
            subject_performance = ExamResult.objects.filter(**year_filter).values(
                'subject__name'
            ).annotate(
                avg_score=Avg('percentage'),
                count=Count('id')
            ).order_by('-avg_score')[:10]

        # Pass rate calculation (D1 to P7 = pass, F9 = fail)
        pass_grade_range = ['D1', 'D2', 'C3', 'C4', 'C5', 'C6', 'P7', 'P8']
        if school:
            total_results = ExamResult.objects.filter(**base_filters, **year_filter).count()
            passed = ExamResult.objects.filter(
                **base_filters, **year_filter, grade__in=pass_grade_range
            ).count()
        else:
            total_results = ExamResult.objects.filter(**year_filter).count()
            passed = ExamResult.objects.filter(
                **year_filter, grade__in=pass_grade_range
            ).count()

        pass_rate = round((passed / total_results * 100), 1) if total_results > 0 else 0

        return Response({
            'grade_distribution': list(grade_dist),
            'class_performance': list(class_performance),
            'subject_performance': list(subject_performance),
            'summary': {
                'total_results': total_results,
                'passed': passed,
                'failed': total_results - passed,
                'pass_rate': pass_rate,
            }
        })


class StudentReportView(APIView):
    """API endpoint for individual student reports."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get student-specific report data."""
        user = request.user
        student_id = request.query_params.get('student_id')

        if not student_id:
            return Response({'error': 'student_id required'}, status=400)

        from students.models import Student
        from academic.models import Enrollment
        from exams.models import ExamResult
        from finance.models import Invoice, Payment
        from attendance.models import DailyAttendance

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)

        # Enrollment history
        enrollments = Enrollment.objects.filter(student=student).select_related(
            'class_obj', 'academic_year', 'term'
        ).order_by('-academic_year__start_date')

        # Exam results
        results = ExamResult.objects.filter(
            student=student
        ).select_related('exam_set', 'subject').order_by('-exam_set__date')

        # Financial history
        invoices = Invoice.objects.filter(
            items__student=student
        ).distinct().order_by('-created_at')[:10]

        # Attendance summary (last 30 days)
        now = datetime.now()
        date_from = now - timedelta(days=30)
        attendance = DailyAttendance.objects.filter(
            student=student,
            date__gte=date_from
        ).aggregate(
            present=Count('id', filter=db_models.Q(status='present')),
            absent=Count('id', filter=db_models.Q(status='absent')),
            late=Count('id', filter=db_models.Q(status='late'))
        )

        return Response({
            'student': {
                'id': student.id,
                'name': str(student),
                'registration_number': student.registration_number,
                'gender': student.gender,
                'current_class': student.current_class.name if student.current_class else None,
            },
            'enrollments': list(enrollments.values(
                'id', 'class_obj__name', 'academic_year__name', 'term__name', 'status'
            )),
            'exam_results': list(results.values(
                'id', 'exam_set__name', 'exam_set__date', 'subject__name',
                'score', 'grade', 'percentage'
            )),
            'attendance_summary': {
                'present': attendance['present'],
                'absent': attendance['absent'],
                'late': attendance['late'],
                'attendance_rate': round(
                    (attendance['present'] / (attendance['present'] + attendance['absent']) * 100), 1
                ) if (attendance['present'] + attendance['absent']) > 0 else 0,
            },
        })
