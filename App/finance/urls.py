"""
URL configuration for Finance app.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FeeStructureViewSet, InvoiceViewSet, PaymentViewSet, CreditViewSet, RefundViewSet

router = DefaultRouter()
router.register(r'fee-structures', FeeStructureViewSet, basename='finance-fee-structure')
router.register(r'invoices', InvoiceViewSet, basename='finance-invoice')
router.register(r'payments', PaymentViewSet, basename='finance-payment')
router.register(r'credits', CreditViewSet, basename='finance-credit')
router.register(r'refunds', RefundViewSet, basename='finance-refund')

urlpatterns = router.urls
