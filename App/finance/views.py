"""
Views for Finance app.
"""

import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db import models as db_models
from .models import FeeStructure, StudentFee, Invoice, InvoiceItem, Payment, Credit, Refund, PaymentAllocation
from .serializers import (
    FeeStructureSerializer, InvoiceSerializer, PaymentSerializer,
    CreditSerializer, RefundSerializer, InvoiceItemSerializer
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

    def perform_create(self, serializer):
        user = self.request.user
        school = getattr(user, 'staff_profile', None).school if hasattr(user, 'staff_profile') else None
        if not school and user.is_superuser:
            # For superusers, require school in data
            school = serializer.validated_data.get('school')
        serializer.save(school=school)


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice model."""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.all()

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by student
        student_id = self.request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(items__student_id=student_id).distinct()

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(invoice_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(invoice_date__lte=date_to)

        if user.is_superuser:
            return queryset
        if hasattr(user, 'staff_profile'):
            return queryset.filter(school=user.staff_profile.school)
        return Invoice.objects.none()

    def create(self, request, *args, **kwargs):
        """Create invoice with nested items."""
        user = request.user
        school = getattr(user, 'staff_profile', None).school if hasattr(user, 'staff_profile') else None

        data = request.data.copy()
        items_data = data.pop('items', [])

        # Generate invoice number
        invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

        # Get parent and calculate total
        parent = data.get('parent')
        total_amount = sum(item.get('amount', 0) for item in items_data)

        invoice = Invoice.objects.create(
            school=school,
            parent_id=parent,
            invoice_number=invoice_number,
            academic_year_id=data.get('academic_year'),
            term_id=data.get('term'),
            total_amount=total_amount,
            due_date=data.get('due_date'),
            notes=data.get('notes', ''),
            status=data.get('status', 'draft')
        )

        # Create invoice items
        for item_data in items_data:
            InvoiceItem.objects.create(
                invoice=invoice,
                student_id=item_data.get('student'),
                description=item_data.get('description'),
                amount=item_data.get('amount'),
                fee_type=item_data.get('fee_type', 'tuition')
            )

        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_items(self, request, pk=None):
        """Add items to an invoice."""
        invoice = self.get_object()
        items_data = request.data.get('items', [])

        for item_data in items_data:
            InvoiceItem.objects.create(
                invoice=invoice,
                student_id=item_data.get('student'),
                description=item_data.get('description'),
                amount=item_data.get('amount'),
                fee_type=item_data.get('fee_type', 'tuition')
            )

        # Update total
        invoice.total_amount = invoice.items.aggregate(total=db_models.Sum('amount'))['total'] or 0
        invoice.save()

        return Response(InvoiceSerializer(invoice).data)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.all()

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by method
        method = self.request.query_params.get('method')
        if method:
            queryset = queryset.filter(payment_method=method)

        # Filter by date
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(payment_date=date)

        if user.is_superuser:
            return queryset
        if hasattr(user, 'staff_profile'):
            return queryset.filter(school=user.staff_profile.school)
        return Payment.objects.none()

    def create(self, request, *args, **kwargs):
        """Create payment and allocate to invoice."""
        user = request.user
        school = getattr(user, 'staff_profile', None).school if hasattr(user, 'staff_profile') else None

        data = request.data.copy()

        payment = Payment.objects.create(
            school=school,
            parent_id=data.get('parent'),
            amount=data.get('amount'),
            payment_date=data.get('payment_date'),
            payment_method=data.get('payment_method'),
            reference=data.get('reference', ''),
            notes=data.get('notes', ''),
            status=data.get('status', 'completed'),
            mobile_phone=data.get('mobile_phone', ''),
            mobile_network=data.get('mobile_network', ''),
            bank_name=data.get('bank_name', ''),
            bank_account=data.get('bank_account', '')
        )

        # Allocate to invoice if provided
        invoice_id = data.get('invoice')
        if invoice_id:
            invoice = get_object_or_404(Invoice, pk=invoice_id)
            PaymentAllocation.objects.create(
                payment=payment,
                invoice=invoice,
                amount=data.get('amount')
            )

            # Update invoice
            invoice.amount_paid = invoice.allocations.aggregate(total=db_models.Sum('amount'))['total'] or 0
            invoice.balance = invoice.total_amount - invoice.amount_paid
            if invoice.balance <= 0:
                invoice.status = 'paid'
            elif invoice.amount_paid > 0:
                invoice.status = 'partial'
            invoice.save()

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
