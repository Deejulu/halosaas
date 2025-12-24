from django.contrib import admin
from .models import Order, OrderItem, Review

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'quantity', 'price', 'total_price')
    fields = ('menu_item', 'quantity', 'price', 'total_price', 'special_requests')
    
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'restaurant', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'restaurant')
    search_fields = ('id', 'customer__username', 'restaurant__name', 'customer_name', 'customer_phone')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'restaurant', 'total_price', 'status')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 'special_instructions')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_pending', 'mark_confirmed', 'mark_preparing', 'mark_ready', 'mark_completed', 'mark_cancelled']
    
    def mark_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} orders marked as Pending.')
    
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} orders marked as Confirmed.')
    
    def mark_preparing(self, request, queryset):
        updated = queryset.update(status='preparing')
        self.message_user(request, f'{updated} orders marked as Preparing.')
    
    def mark_ready(self, request, queryset):
        updated = queryset.update(status='ready')
        self.message_user(request, f'{updated} orders marked as Ready.')
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} orders marked as Completed.')
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} orders marked as Cancelled.')
    
    # Set short descriptions for all actions
    for action in [mark_pending, mark_confirmed, mark_preparing, mark_ready, mark_completed, mark_cancelled]:
        action.short_description = f"Mark selected orders as {action.__name__.replace('mark_', '').title()}"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price', 'total_price')
    list_filter = ('order__restaurant',)
    search_fields = ('order__id', 'menu_item__name')
    
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'customer', 'restaurant', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at', 'restaurant')
    search_fields = ('customer__username', 'restaurant__name', 'comment')
    list_editable = ('is_approved', 'rating')
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews disapproved.')
    disapprove_reviews.short_description = "Disapprove selected reviews"