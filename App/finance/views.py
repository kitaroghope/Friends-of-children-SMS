"""
Views for Finance app.
"""

from rest_framework import viewsets, permissions
from .models import FeeStructure, Invoice, Payment, Credit, Refund
from .serializers import (
    FeeStructureSerializer, InvoiceSerializer, PaymentSerializer,
    CreditSerializer, RefundSerializer
)


class FeeStructureViewSet(viewsets.ModelViewSet):
    """ViewSet for FeeStructure model."""
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return FeeStructure.objects.all()
        if hasattr(user, 'staff_profile'):
            return FeeStructure.objects.filter(school=user.staff_profile.school)
        return FeeStructure.objects.none()


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice model."""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Invoice.objects.all()
        if hasattr(user, 'staff_profile'):
            return Invoice.objects.filter(school=user.staff_profile.school)
        return Invoice.objects.none()


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        if hasattr(user, 'staff_profile'):
            return Payment.objects.filter(school=user.staff_profile.school)
        return Payment.objects.none()


class CreditViewSet(viewsets.ModelViewSet):
    """ViewSet for Credit model."""
    queryset = Credit.objects.all()
    serializer_class = CreditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Credit.objects.all()
        if hasattr(user, 'staff_profile'):
            return Credit.objects.filter(school=user.staff_profile.school)
        return Credit.objects.none()


class RefundViewSet(viewsets.ModelViewSet):
    """ViewSet for Refund model."""
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Refund.objects.all()
        if hasattr(user, 'staff_profile'):
            return Refund.objects.filter(school=user.staff_profile.school)
        return Refund.objects.none()
