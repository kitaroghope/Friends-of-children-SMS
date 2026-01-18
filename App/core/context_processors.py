"""
Template context processors.
"""

from django.conf import settings


def school_context(request):
    """
    Add school context to all templates.
    Provides current school information if available.
    """
    context = {
        'sms_default_currency': getattr(settings, 'SMS_DEFAULT_CURRENCY', 'UGX'),
    }

    # Add current school if user is authenticated and has one
    if request.user.is_authenticated:
        if hasattr(request.user, 'current_school'):
            context['current_school'] = request.current_school
        elif hasattr(request.user, 'staff_profile'):
            context['current_school'] = request.user.staff_profile.school
        elif hasattr(request.user, 'parent_profile'):
            context['current_school'] = request.user.parent_profile.school

    return context
