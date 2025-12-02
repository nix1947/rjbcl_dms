from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings
from tinymce.models import HTMLField
from dms.common import FISCAL_YEAR_CHOICES



class InsuranceClaimAndLoan(models.Model):
    """Model for storing life insurance claim records"""

    # Claim Type Choices
    CLAIM_TYPE_CHOICES = [
        ('surrender', 'Surrender'),
        ('maturity', 'Maturity'),
        ('death', 'Death Claim'),
        ('foreign_employment', 'Foreign Employment Claim'),
        ('Loan', 'Loan'),

    ]

    # Policy Type Choices
    POLICY_TYPE_CHOICES = [
        ('individual', 'Individual Policy'),
        ('term', 'Term Policy'),
        ('group', 'Group Policy'),
        ('group_transfer', 'Group Transfer Policy'),
        ('rastra_sewak', 'Rastra Sewak Transfer Policy'),
        ('foreign_employment', 'Foreign Employment Policy'),
        ('Loan', 'Loan'),


    ]

    # Basic Information
    policy_no = models.CharField(
        max_length=50,
        verbose_name="Policy Number",
        db_index=True
    )

    claim_type = models.CharField(
        max_length=20,
        choices=CLAIM_TYPE_CHOICES,
        verbose_name="Claim Type"
    )

    policy_type = models.CharField(
        max_length=20,
        choices=POLICY_TYPE_CHOICES,
        verbose_name="Policy Type"
    )

    # Claimant Information
    claim_name = models.CharField(
        max_length=200,
        verbose_name="Claimant Name"
    )

    claim_phone = models.CharField(
        max_length=20,
        verbose_name="Phone",
        blank=True
    )

    claim_email = models.EmailField(
        verbose_name="Email",
        blank=True
    )

    # Claim Details
    claim_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Claim Amount"
    )

    claim_payment_date = models.DateField(
        verbose_name="Payment Date"
    )

    voucher_no = models.CharField(
        max_length=50,
        verbose_name="Voucher Number"
    )

    # Document Uploads
    claim_document = models.FileField(
        upload_to='claims/documents/%Y/%m/',
        verbose_name="Claim Document",
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        help_text="Upload claim bag document"
    )

    payment_voucher = models.FileField(
        upload_to='claims/vouchers/%Y/%m/',
        verbose_name="Payment Voucher",
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        help_text="Upload payment voucher"
    )

    # Additional Information
    remarks =HTMLField(
        blank=True,
        null=True,
        verbose_name="Remarks"
    )

    fiscal_year = models.CharField(
        max_length=10,
        verbose_name="Fiscal Year",
        blank=True,
        help_text="e.g., 2080/81",
        choices=FISCAL_YEAR_CHOICES
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='insurance_claims',
        verbose_name="Created By"
    )

    class Meta:
        ordering = ['-claim_payment_date', '-created_at']
        verbose_name = "Insurance Claim"
        verbose_name_plural = "Upload Insurance Claims and Loan Bags"
        indexes = [
            models.Index(fields=['policy_no', 'claim_type']),
            models.Index(fields=['claim_payment_date']),
        ]

    def __str__(self):
        return f"{self.policy_no} - {self.claim_name} - {self.get_claim_type_display()}"