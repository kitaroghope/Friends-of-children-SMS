"""
Middleware for audit logging.
"""

import json
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.conf import settings
from .models import AuditLog


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to track all requests for audit purposes.
    Only logs when AUDIT_LOG_ENABLED is True.
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.enabled = getattr(settings, 'AUDIT_LOG_ENABLED', True)
        self.exclude_paths = getattr(settings, 'AUDIT_LOG_EXCLUDE_PATHS', [])

    def __call__(self, request):
        # Skip if audit logging is disabled
        if not self.enabled:
            return self.get_response(request)

        # Skip excluded paths
        path = request.path
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return self.get_response(request)

        # Store start time
        request._audit_start_time = timezone.now()

        response = self.get_response(request)

        # Log the request after processing
        self._log_request(request, response)

        return response

    def _log_request(self, request, response):
        """Log the request details."""
        try:
            # Only log significant actions (status codes 200-299 for POST/PUT/PATCH/DELETE)
            if request.method in ('GET', 'HEAD'):
                return

            if not 200 <= response.status_code < 300:
                return

            # Determine action type from HTTP method
            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete',
            }
            action = action_map.get(request.method, 'update')

            # Try to get user and school from request
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            school = None
            if hasattr(request, 'current_school'):
                school = request.current_school

            AuditLog.objects.create(
                user=user,
                school=school,
                action=action,
                model_name=self._get_model_name(request),
                object_id=self._get_object_id(request),
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                is_offline=getattr(request, 'is_offline', False),
                sync_batch_id=getattr(request, 'sync_batch_id', None),
            )
        except Exception:
            # Don't let audit logging break the application
            pass

    def _get_model_name(self, request):
        """Extract model name from URL path."""
        path = request.path.strip('/')
        parts = path.split('/')
        if len(parts) >= 2:
            # Typical API pattern: /api/{app}/{model}/
            return parts[1] if parts[0] == 'api' else parts[0]
        return path

    def _get_object_id(self, request):
        """Extract object ID from URL path."""
        path = request.path.strip('/')
        parts = path.split('/')
        if len(parts) >= 3:
            # Try to extract ID from URL like /api/model/123/
            try:
                int(parts[2])
                return str(parts[2])
            except ValueError:
                pass
        return None

    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
