"""
Views for Promotion app.
"""

from rest_framework import viewsets, permissions
from .models import PromotionRule, PromotionRecord
from .serializers import PromotionRuleSerializer, PromotionRecordSerializer


class PromotionRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for PromotionRule model."""
    queryset = PromotionRule.objects.all()
    serializer_class = PromotionRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return PromotionRule.objects.all()
        if hasattr(user, 'staff_profile'):
            return PromotionRule.objects.filter(school=user.staff_profile.school)
        return PromotionRule.objects.none()


class PromotionRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for PromotionRecord model."""
    queryset = PromotionRecord.objects.all()
    serializer_class = PromotionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return PromotionRecord.objects.all()
        if hasattr(user, 'staff_profile'):
            return PromotionRecord.objects.filter(school=user.staff_profile.school)
        return PromotionRecord.objects.none()
