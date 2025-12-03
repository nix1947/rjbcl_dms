from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import InsuranceClaimAndLoan
from decimal import Decimal


@admin.register(InsuranceClaimAndLoan)
class InsuranceClaimAdmin(admin.ModelAdmin):
    list_display = [
        'policy_no',
        'claim_name',
        'claim_type',
        'claim_amount_display',
        'lock',
        'claim_payment_date',
        'claim_document_link',
        'voucher_link',
        'created_at',
    ]

    list_filter = [
        'claim_type',
        'policy_type',
        'claim_payment_date',
        'fiscal_year',
        'created_at',
    ]

    search_fields = [
        'policy_no',
        'voucher_no',
        'claim_name',
        'claim_phone',
        'claim_email',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'document_preview',
    ]

    fieldsets = (
        ('Policy Information', {
            'fields': (
                'policy_no',
                'policy_type',
                'fiscal_year',
            )
        }),
        ('Claimant Details', {
            'fields': (
                'claim_name',
                'claim_phone',
                'claim_email',
            )
        }),
        ('Claim Information', {
            'fields': (
                'claim_type',
                'claim_amount',
                'claim_payment_date',
                'voucher_no',
            )
        }),
        ('Documents', {
            'fields': (
                'claim_document',
                'payment_voucher',
                'document_preview',
                'lock',
            )
        }),
        ('Additional Information', {
            'fields': ('remarks',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': (
                'created_at',
                'updated_at',
                'created_by',
            ),
            'classes': ('collapse',)
        }),
    )

    date_hierarchy = 'claim_payment_date'
    list_per_page = 50

    # Allow delete only for superusers (and respect lock)
    def has_delete_permission(self, request, obj=None):
        if obj and getattr(obj, 'lock', False):
            return False
        return request.user.is_superuser

    # --- Links and preview ---

    def claim_document_link(self, obj):
        if obj.claim_document:
            return format_html('<a href="{}" target="_blank">⬇ Doc</a>', obj.claim_document.url)
        return "-"
    claim_document_link.short_description = 'Doc'

    def voucher_link(self, obj):
        if obj.payment_voucher:
            return format_html('<a href="{}" target="_blank">⬇ Voucher</a>', obj.payment_voucher.url)
        return "-"
    voucher_link.short_description = 'Voucher'

    def claim_amount_display(self, obj):
        """
        Format the numeric value BEFORE calling format_html so we never try to apply a numeric
        format specifier to a SafeString (or non-numeric type).
        """
        amount = getattr(obj, 'claim_amount', None)

        # handle None or non-numeric safely
        if amount is None:
            formatted = "0.00"
        else:
            # If Decimal or numeric, format with thousand separators and 2 decimal places
            try:
                # use Decimal for consistent formatting if possible
                if not isinstance(amount, (int, float, Decimal)):
                    # try to coerce numeric strings to Decimal
                    amount = Decimal(str(amount))
                formatted = f"{amount:,.2f}"
            except Exception:
                # fallback: str()
                formatted = str(amount)

        # Now pass only a plain string into format_html
        return format_html('<strong>Rs. {}</strong>', formatted)

    claim_amount_display.short_description = 'Claim Amount'
    claim_amount_display.admin_order_field = 'claim_amount'

    def document_preview(self, obj):
        """Return preview links (safe) — we do not include numeric format specifiers here."""
        if not obj or (not getattr(obj, 'claim_document', None) and not getattr(obj, 'payment_voucher', None)):
            return format_html('<em>No documents</em>')

        parts = []
        if getattr(obj, 'claim_document', None):
            parts.append(
                format_html(
                    '<div style="margin-bottom:6px;"><strong>Claim Document:</strong> <a href="{}" target="_blank">📄 View Claim Document</a></div>',
                    obj.claim_document.url
                )
            )
        if getattr(obj, 'payment_voucher', None):
            parts.append(
                format_html(
                    '<div><strong>Payment Voucher:</strong> <a href="{}" target="_blank">📄 View Payment Voucher</a></div>',
                    obj.payment_voucher.url
                )
            )

        return format_html(''.join(parts))

    document_preview.short_description = 'Document Links'

    # Make everything readonly when locked
    def get_readonly_fields(self, request, obj=None):
        if obj and getattr(obj, 'lock', False):
            # return all model field names + our custom preview
            return [f.name for f in obj._meta.fields] + ['document_preview']
        return super().get_readonly_fields(request, obj)

    # Save model to capture creator
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
