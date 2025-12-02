from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import InsuranceClaimAndLoan


@admin.register(InsuranceClaimAndLoan)
class InsuranceClaimAdmin(admin.ModelAdmin):
    """Admin interface for Insurance Claims"""

    # List Display
    list_display = [
        'policy_no',
        'claim_name',
        'claim_type',
        'policy_type',
        'claim_amount_display',
        'claim_payment_date',
        'voucher_no',
        'created_at',
    ]

    # Filters
    list_filter = [
        'claim_type',
        'policy_type',
        'claim_payment_date',
        'fiscal_year',
        'created_at',
    ]

    # Search
    search_fields = [
        'policy_no',
        'voucher_no',
        'claim_name',
        'claim_phone',
        'claim_email',
    ]

    # Readonly fields
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'document_preview',
    ]

    # Field organization
    fieldsets = (
        ('Policy Information', {
            'fields': (
                'policy_no',
                'policy_type',
                'fiscal_year',
            )
        }),
        ('Claim Details', {
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

    # Date hierarchy
    date_hierarchy = 'claim_payment_date'

    # Items per page
    list_per_page = 50

    # Custom display methods
    def claim_amount_display(self, obj):
        """Format claim amount with currency"""
        return format_html(
            '<strong style="color: #007bff;">Rs. {:,.2f}</strong>',
            obj.claim_amount
        )

    claim_amount_display.short_description = 'Claim Amount'
    claim_amount_display.admin_order_field = 'claim_amount'

    def document_preview(self, obj):
        """Preview uploaded documents"""
        html = '<div style="margin: 10px 0;">'

        if obj.claim_document:
            html += f'''
            <div style="margin-bottom: 10px;">
                <strong>Claim Document:</strong><br>
                <a href="{obj.claim_document.url}" target="_blank" style="color: #007bff;">
                    📄 View Claim Document
                </a>
            </div>
            '''

        if obj.payment_voucher:
            html += f'''
            <div>
                <strong>Payment Voucher:</strong><br>
                <a href="{obj.payment_voucher.url}" target="_blank" style="color: #007bff;">
                    📄 View Payment Voucher
                </a>
            </div>
            '''

        html += '</div>'
        return format_html(html) if (obj.claim_document or obj.payment_voucher) else format_html(
            '<em>No documents</em>')

    document_preview.short_description = 'Document Links'

    # Actions
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        """Export selected claims to CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="insurance_claims.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Policy No',
            'Claim  Name',
            'Claim Type',
            'Policy Type',
            'Claim Amount',
            'Payment Date',
            'Voucher No',
            'Phone',
            'Email',
            'Fiscal Year',
            'Created At',
        ])

        for claim in queryset:
            writer.writerow([
                claim.policy_no,
                claim.claim_name,
                claim.get_claim_type_display(),
                claim.get_policy_type_display(),
                claim.claim_amount,
                claim.claim_payment_date,
                claim.voucher_no,
                claim.claim_phone,
                claim.claim_email,
                claim.fiscal_year,
                claim.created_at.strftime('%Y-%m-%d %H:%M'),
            ])

        return response

    export_as_csv.short_description = 'Export to CSV'

    # Custom changelist view with statistics
    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to the changelist"""
        extra_context = extra_context or {}

        # Get statistics
        stats = InsuranceClaimAndLoan.objects.aggregate(
            total_claims=Count('id'),
            total_amount=Sum('claim_amount'),
        )

        extra_context['total_claims'] = stats['total_claims'] or 0
        extra_context['total_amount'] = stats['total_amount'] or 0

        return super().changelist_view(request, extra_context)

    # Save method to capture user
    def save_model(self, request, obj, form, change):
        """Save the created_by field"""
        if not change:  # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)