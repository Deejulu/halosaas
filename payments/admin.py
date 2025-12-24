from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('id', 'order__id', 'reference')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'amount', 'status', 'payment_method')
        }),
        ('Transaction Details', {
            'fields': ('reference', 'transaction_id', 'payment_details')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_success', 'mark_failed', 'mark_pending']
    
    def mark_success(self, request, queryset):
        updated = queryset.update(status='success')
        self.message_user(request, f'{updated} payments marked as Success.')
    mark_success.short_description = "Mark selected payments as Success"
    
    def mark_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} payments marked as Failed.')
    mark_failed.short_description = "Mark selected payments as Failed"
    
    def mark_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} payments marked as Pending.')
    mark_pending.short_description = "Mark selected payments as Pending"