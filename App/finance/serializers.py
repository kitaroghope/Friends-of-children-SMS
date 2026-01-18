"""
Serializers for Finance app.
"""

from rest_framework import serializers
from .models import FeeStructure, StudentFee, Invoice, InvoiceItem, Payment, Credit, Refund


class FeeStructureSerializer(serializers.ModelSerializer):
    """Serializer for FeeStructure model."""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)

    class Meta:
        model = FeeStructure
        fields = [
            'id', 'school', 'class_obj', 'class_name', 'academic_year',
            'term', 'name', 'description', 'amount', 'due_date',
            'is_compulsory', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'school', 'parent', 'parent_name', 'invoice_number',
            'academic_year', 'term', 'total_amount', 'amount_paid',
            'balance', 'status', 'issue_date', 'due_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_amount', 'amount_paid', 'balance', 'issue_date', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'school', 'parent', 'parent_name', 'amount',
            'payment_date', 'payment_method', 'reference',
            'received_by', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class CreditSerializer(serializers.ModelSerializer):
    """Serializer for Credit model."""
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)

    class Meta:
        model = Credit
        fields = [
            'id', 'school', 'parent', 'parent_name', 'amount',
            'source', 'reference', 'description', 'remaining_amount',
            'is_active', 'expires_at', 'created_at'
        ]
        read_only_fields = ['remaining_amount', 'created_at']


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for Refund model."""
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'school', 'parent', 'parent_name', 'payment', 'credit',
            'amount', 'reason', 'status', 'requested_by', 'approved_by',
            'approved_at', 'processed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['approved_at', 'processed_at', 'created_at', 'updated_at']
