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

urlpatterns = [
    path('', home, name='home'),
    path('register/school/', register_school, name='register_school'),
    path('register/', register_user, name='register_user'),
    path('onboard/staff/', onboard_staff, name='onboard_staff'),
    path('onboard/parent/', onboard_parent, name='onboard_parent'),
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
