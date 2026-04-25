"""
Finance models for the SMS system.
Handles fees, invoices, payments, credits, and refunds.
"""

import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from core.models import BaseModel, School


class FeeStructure(BaseModel):
    """
    Fee structure for a class per term.
    """
    CATEGORY_CHOICES = [
        ('tuition', 'Tuition'),
        ('meals', 'Meals'),
        ('transport', 'Transport'),
        ('uniform', 'Uniform'),
        ('books', 'Books'),
        ('other', 'Other'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fee_structures')
    class_obj = models.ForeignKey(
        'academic.Class',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    academic_year = models.ForeignKey(
        'schools.AcademicYear',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    term = models.ForeignKey(
        'schools.Term',
        on_delete=models.CASCADE,
        related_name='fee_structures'
    )
    name = models.CharField(max_length=100, help_text="e.g., Term 1 Tuition, Activity Fee")
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='tuition')
    is_compulsory = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive'), ('draft', 'Draft')], default='active')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['academic_year', 'term', 'name']

    def __str__(self):
        return f"{self.class_obj.name} - {self.name}: {self.amount}"


class StudentFee(BaseModel):
    """
    Fee assigned to a student with optional discount.
    """
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='student_fees'
    )
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name='student_fees'
    )
    original_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_reason = models.TextField(blank=True)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fee_structure', 'student']

    def __str__(self):
        return f"{self.student} - {self.fee_structure.name}: {self.final_amount}"

    def clean(self):
        """Validate discount doesn't exceed original amount."""
        if self.discount_amount > self.original_amount:
            raise ValidationError('Discount cannot exceed original amount.')

    def save(self, *args, **kwargs):
        """Calculate final amount."""
        self.final_amount = self.original_amount - self.discount_amount
        super().save(*args, **kwargs)


class Invoice(BaseModel):
    """
    Invoice for a parent (may include multiple students).
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='invoices')
    parent = models.ForeignKey(
        'parents.ParentProfile',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    invoice_number = models.CharField(max_length=50)
    academic_year = models.ForeignKey(
        'schools.AcademicYear',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    term = models.ForeignKey(
        'schools.Term',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    invoice_date = models.DateField(default=datetime.date.today)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.parent}"

    def save(self, *args, **kwargs):
        """Calculate balance."""
        self.balance = self.total_amount - self.amount_paid
        if self.balance == 0 and self.amount_paid > 0:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        super().save(*args, **kwargs)


class InvoiceItem(BaseModel):
    """
    Individual item in an invoice.
    """
    FEE_TYPE_CHOICES = [
        ('tuition', 'Tuition'),
        ('meals', 'Meals'),
        ('transport', 'Transport'),
        ('uniform', 'Uniform'),
        ('books', 'Books'),
        ('other', 'Other'),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='invoice_items'
    )
    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name='invoice_items',
        null=True,
        blank=True
    )
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default='tuition')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['invoice', 'student']

    def __str__(self):
        return f"{self.invoice} - {self.student}: {self.amount}"


class Payment(BaseModel):
    """
    Payment from a parent.
    """
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('mobile', 'Mobile Money'),
        ('card', 'Card'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='payments')
    parent = models.ForeignKey(
        'parents.ParentProfile',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    received_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments_received'
    )
    notes = models.TextField(blank=True)

    # Mobile money specific
    mobile_phone = models.CharField(max_length=20, blank=True)
    mobile_network = models.CharField(max_length=20, blank=True)

    # Bank transfer specific
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"Payment {self.amount} by {self.parent} on {self.payment_date}"


class PaymentAllocation(BaseModel):
    """
    Allocation of payment to invoice(s).
    """
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    allocated_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    allocated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['invoice', 'payment']

    def __str__(self):
        return f"{self.payment} -> {self.invoice}: {self.amount}"


class Credit(BaseModel):
    """
    Credit balance for a parent (from overpayment or refund).
    """
    SOURCE_CHOICES = [
        ('overpayment', 'Overpayment'),
        ('refund', 'Refund'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='credits')
    parent = models.ForeignKey(
        'parents.ParentProfile',
        on_delete=models.CASCADE,
        related_name='credits'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    reference = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Credit {self.amount} for {self.parent}"

    def save(self, *args, **kwargs):
        """Initialize remaining amount."""
        if not self.pk:
            self.remaining_amount = self.amount
        super().save(*args, **kwargs)


class Refund(BaseModel):
    """
    Refund to a parent.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='refunds')
    parent = models.ForeignKey(
        'parents.ParentProfile',
        on_delete=models.CASCADE,
        related_name='refunds'
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds'
    )
    credit = models.ForeignKey(
        Credit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds_requested'
    )
    approved_by = models.ForeignKey(
        'staff.StaffProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refunds_approved'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund {self.amount} for {self.parent}"
