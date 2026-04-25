"""
Views for Staff app.
"""

from rest_framework import viewsets, permissions
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import StaffProfile
from .serializers import StaffProfileSerializer


class StaffProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for StaffProfile model."""
    queryset = StaffProfile.objects.all()
    serializer_class = StaffProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return StaffProfile.objects.all()
        if hasattr(user, 'staff_profile'):
            return StaffProfile.objects.filter(school=user.staff_profile.school)
        return StaffProfile.objects.none()


def my_profile_view(request):
    """Display and edit current user's staff profile."""
    user = request.user

    if not hasattr(user, 'staff_profile'):
        messages.error(request, 'You do not have a staff profile')
        return redirect('/dashboard/')

    staff = user.staff_profile

    if request.method == 'POST':
        # Update staff profile
        staff.first_name = request.POST.get('first_name', staff.first_name)
        staff.last_name = request.POST.get('last_name', staff.last_name)
        staff.phone = request.POST.get('phone', staff.phone)
        staff.email = request.POST.get('email', staff.email)
        staff.department = request.POST.get('department', staff.department)
        staff.position = request.POST.get('position', staff.position)
        staff.gender = request.POST.get('gender', staff.gender)
        staff.address = request.POST.get('address', staff.address)
        staff.emergency_contact = request.POST.get('emergency_contact', staff.emergency_contact)
        staff.notes = request.POST.get('notes', staff.notes)
        staff.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('/staff/profile/')

    return render(request, 'staff/profile.html', {'staff': staff})
