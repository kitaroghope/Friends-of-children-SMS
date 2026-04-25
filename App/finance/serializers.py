"""
Serializers for Finance app.
"""

from rest_framework import serializers
from .models import FeeStructure, StudentFee, Invoice, InvoiceItem, Payment, Credit, Refund


class FeeStructureSerializer(serializers.ModelSerializer):
    """Serializer for FeeStructure model."""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    category = serializers.SerializerMethodField()

    class Meta:
        model = FeeStructure
        fields = [
            'id', 'school', 'class_obj', 'class_name', 'academic_year', 'academic_year_name',
            'term', 'name', 'description', 'amount', 'due_date',
            'is_compulsory', 'is_active', 'category', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_category(self, obj):
        # Map fee name to category for UI filtering
        name_lower = obj.name.lower()
        if 'tuition' in name_lower:
            return 'tuition'
        elif 'meal' in name_lower or 'food' in name_lower:
            return 'meals'
        elif 'transport' in name_lower or 'bus' in name_lower:
            return 'transport'
        elif 'uniform' in name_lower or 'cloth' in name_lower:
            return 'uniform'
        elif 'book' in name_lower or 'material' in name_lower:
            return 'books'
        return 'other'


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)
    student_name = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'school', 'parent', 'parent_name', 'student_name', 'invoice_number',
            'academic_year', 'term', 'total_amount', 'amount_paid',
            'balance', 'status', 'invoice_date', 'due_date', 'notes',
            'items', 'payments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_amount', 'amount_paid', 'balance', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        # Get first student name from invoice items
        first_item = obj.items.first()
        if first_item:
            return f"{first_item.student.first_name} {first_item.student.last_name}"
        return None

    def get_payments(self, obj):
        # Get allocations for this invoice
        from finance.models import PaymentAllocation
        allocations = PaymentAllocation.objects.filter(invoice=obj)
        return PaymentAllocationSerializer(allocations, many=True).data

    def get_items(self, obj):
        return InvoiceItemSerializer(obj.items.all(), many=True).data


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for InvoiceItem model."""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)

    class Meta:
        model = InvoiceItem
        fields = ['id', 'student', 'student_name', 'description', 'amount', 'fee_type']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    parent_name = serializers.CharField(source='parent.get_full_name', read_only=True)
    student_name = serializers.SerializerMethodField()
    receipt_number = serializers.SerializerMethodField()
    invoice_number = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'school', 'parent', 'parent_name', 'student_name',
            'amount', 'payment_date', 'payment_method', 'reference',
            'received_by', 'notes', 'status',
            'receipt_number', 'invoice_number',
            'mobile_phone', 'mobile_network', 'bank_name', 'bank_account',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def get_student_name(self, obj):
        from finance.models import PaymentAllocation
        alloc = obj.allocations.first()
        if alloc:
            first_item = alloc.invoice.items.first()
            if first_item:
                return f"{first_item.student.first_name} {first_item.student.last_name}"
        return None

    def get_receipt_number(self, obj):
        return f"RCP-{obj.id:06d}"

    def get_invoice_number(self, obj):
        alloc = obj.allocations.first()
        if alloc:
            return alloc.invoice.invoice_number
        return None


class PaymentAllocationSerializer(serializers.ModelSerializer):
    """Serializer for PaymentAllocation model."""
    class Meta:
        from .models import PaymentAllocation
        model = PaymentAllocation
        fields = ['id', 'amount', 'allocated_at']


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
