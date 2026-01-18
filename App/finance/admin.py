"""
Admin configuration for Finance app.
"""

from django.contrib import admin
from .models import FeeStructure, StudentFee, Invoice, InvoiceItem, Payment, PaymentAllocation, Credit, Refund


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['school', 'class_obj', 'academic_year', 'term', 'name', 'amount', 'is_compulsory']
    list_filter = ['school', 'academic_year', 'term', 'is_compulsory']


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_structure', 'original_amount', 'discount_amount', 'final_amount']
    list_filter = ['school', 'fee_structure']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'parent', 'academic_year', 'term', 'total_amount', 'amount_paid', 'balance', 'status']
    list_filter = ['school', 'academic_year', 'term', 'status']
    search_fields = ['invoice_number', 'parent__first_name', 'parent__last_name']


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'student', 'description', 'amount']
    list_filter = ['school']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['parent', 'amount', 'payment_date', 'payment_method', 'reference', 'received_by']
    list_filter = ['school', 'payment_method', 'payment_date']
    search_fields = ['parent__first_name', 'parent__last_name', 'reference']


@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ['payment', 'invoice', 'amount', 'allocated_by']
    list_filter = ['school']


@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ['parent', 'amount', 'remaining_amount', 'source', 'is_active']
    list_filter = ['school', 'source', 'is_active']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['parent', 'amount', 'reason', 'status', 'requested_by', 'approved_by']
    list_filter = ['school', 'status']
    readonly_fields = ['requested_by', 'approved_by', 'approved_at', 'processed_at']
