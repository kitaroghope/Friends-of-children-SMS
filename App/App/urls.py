"""
URL configuration for App project.
Multi-School School Management System
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def home(request):
    """Welcome page with quick links."""
    return render(request, 'home.html')

def register_school(request):
    """School registration page."""
    return render(request, 'register_school.html')

def register_user(request):
    """User registration page."""
    return render(request, 'register_user.html')

def onboard_staff(request):
    """Staff onboarding page for school admins."""
    return render(request, 'onboard_staff.html')

def onboard_parent(request):
    """Parent onboarding page for school staff."""
    return render(request, 'onboard_parent.html')

def my_profile(request):
    """My staff profile page."""
    from staff.views import my_profile_view
    return my_profile_view(request)

def login_view(request):
    """Login page."""
    return render(request, 'auth/login.html')

def logout_view(request):
    """Logout and redirect to home."""
    from django.contrib.auth import logout
    logout(request)
    return render(request, 'home.html')

def dashboard_view(request):
    """Main dashboard."""
    return render(request, 'dashboard/home.html')

def setup_wizard_view(request):
    """School setup wizard."""
    return render(request, 'setup/wizard.html')

def students_view(request):
    """Student list."""
    return render(request, 'students/list.html')

def student_add_view(request):
    """Add student."""
    return render(request, 'students/add.html')

def student_enroll_view(request):
    """Enroll student."""
    return render(request, 'students/enroll.html')

def staff_view(request):
    """Staff list."""
    return render(request, 'staff/list.html')

def staff_add_view(request):
    """Add staff."""
    return render(request, 'staff/add.html')

def parents_view(request):
    """Parent list."""
    return render(request, 'parents/list.html')

def parent_add_view(request):
    """Add parent."""
    return render(request, 'parents/add.html')

def parent_link_view(request):
    """Link parent to student."""
    return render(request, 'parents/link.html')

def classes_view(request):
    """Class management."""
    return render(request, 'academic/classes.html')

def subjects_view(request):
    """Subject management."""
    return render(request, 'academic/subjects.html')

def exam_sets_view(request):
    """Exam sets."""
    return render(request, 'exams/sets.html')

def exam_results_view(request):
    """Exam results."""
    return render(request, 'exams/results.html')

def exam_reports_view(request):
    """Exam reports."""
    return render(request, 'exams/reports.html')

def fees_view(request):
    """Fee structures."""
    return render(request, 'finance/fees.html')

def invoices_view(request):
    """Invoices."""
    return render(request, 'finance/invoices.html')

def payments_view(request):
    """Payments."""
    return render(request, 'finance/payments.html')

def reports_view(request):
    """Reports."""
    return render(request, 'reports/index.html')

urlpatterns = [
    path('', home, name='home'),
    path('register/school/', register_school, name='register_school'),
    path('register/', register_user, name='register_user'),
    path('onboard/staff/', onboard_staff, name='onboard_staff'),
    path('onboard/parent/', onboard_parent, name='onboard_parent'),

    # Auth & Dashboard
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # Setup
    path('setup/wizard/', setup_wizard_view, name='setup_wizard'),

    # Students
    path('students/', students_view, name='students'),
    path('students/add/', student_add_view, name='student_add'),
    path('students/enroll/', student_enroll_view, name='student_enroll'),

    # Staff
    path('staff/', staff_view, name='staff'),
    path('staff/add/', staff_add_view, name='staff_add'),
    path('staff/profile/', my_profile, name='my_profile'),

    # Parents
    path('parents/', parents_view, name='parents'),
    path('parents/add/', parent_add_view, name='parent_add'),
    path('parents/link/', parent_link_view, name='parent_link'),

    # Academic
    path('academic/classes/', classes_view, name='classes'),
    path('academic/subjects/', subjects_view, name='subjects'),

    # Exams
    path('exams/sets/', exam_sets_view, name='exam_sets'),
    path('exams/results/', exam_results_view, name='exam_results'),
    path('exams/reports/', exam_reports_view, name='exam_reports'),

    # Finance
    path('finance/fees/', fees_view, name='fees'),
    path('finance/invoices/', invoices_view, name='invoices'),
    path('finance/payments/', payments_view, name='payments'),

    # Reports
    path('reports/', reports_view, name='reports'),

    # Admin & API
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/schools/', include('schools.urls')),
    path('api/academic/', include('academic.urls')),
    path('api/students/', include('students.urls')),
    path('api/staff/', include('staff.urls')),
    path('api/parents/', include('parents.urls')),
    path('api/permissions/', include('permissions.urls')),
    path('api/exams/', include('exams.urls')),
    path('api/promotion/', include('promotion.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/offline/', include('offline.urls')),
    path('api/reports/', include('reports.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin site customization
admin.site.site_header = "Friends of Children SMS"
admin.site.site_title = "SMS Admin"
admin.site.index_title = "School Management System"
