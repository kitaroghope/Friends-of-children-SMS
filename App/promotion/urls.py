"""
URL configuration for Promotion app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PromotionRuleViewSet, PromotionRecordViewSet

router = DefaultRouter()
router.register(r'rules', PromotionRuleViewSet, basename='promotion-rule')
router.register(r'records', PromotionRecordViewSet, basename='promotion-record')

urlpatterns = router.urls
