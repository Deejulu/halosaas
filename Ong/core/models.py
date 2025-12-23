from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


# ============================================
# PLATFORM SETTINGS (Singleton Pattern)
# ============================================
class PlatformSettings(models.Model):
    """Global platform configuration - only one instance should exist"""
    
    # Site Branding
    site_name = models.CharField(max_length=100, default="Restaurant SaaS")
    site_tagline = models.CharField(max_length=200, default="Order delicious food from your favorite restaurants")
    support_email = models.EmailField(default="support@example.com")
    support_phone = models.CharField(max_length=20, default="+234 000 000 0000")
    
    # Commission & Fees
    commission_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.00,
        help_text="Platform commission percentage on each order"
    )
    minimum_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=500.00,
        help_text="Minimum order amount allowed"
    )
    delivery_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=500.00,
        help_text="Default delivery fee"
    )
    free_delivery_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=5000.00,
        help_text="Order amount for free delivery (0 to disable)"
    )
    
    # Payment Settings
    payment_gateway = models.CharField(
        max_length=50, default="paystack",
        choices=[('paystack', 'Paystack'), ('flutterwave', 'Flutterwave'), ('stripe', 'Stripe')]
    )
    currency = models.CharField(max_length=3, default="NGN")
    currency_symbol = models.CharField(max_length=5, default="₦")
    
    # Order Settings
    enable_delivery = models.BooleanField(default=True, help_text="Allow delivery orders")
    enable_pickup = models.BooleanField(default=True, help_text="Allow pickup orders")
    enable_dine_in = models.BooleanField(default=False, help_text="Allow dine-in orders")
    max_order_items = models.PositiveIntegerField(default=50, help_text="Maximum items per order")
    order_timeout_minutes = models.PositiveIntegerField(default=30, help_text="Minutes before pending order auto-cancels")
    
    # Feature Toggles
    allow_guest_checkout = models.BooleanField(default=False)
    require_email_verification = models.BooleanField(default=False)
    enable_reviews = models.BooleanField(default=True)
    enable_promo_codes = models.BooleanField(default=True)
    auto_approve_restaurants = models.BooleanField(default=True)
    enable_reservations = models.BooleanField(default=True, help_text="Allow table reservations")
    enable_notifications = models.BooleanField(default=True, help_text="Enable email notifications")
    enable_sms_notifications = models.BooleanField(default=False, help_text="Enable SMS notifications")
    
    # Registration Settings
    allow_customer_registration = models.BooleanField(default=True, help_text="Allow new customer signups")
    allow_restaurant_registration = models.BooleanField(default=True, help_text="Allow new restaurant signups")
    
    # Display Settings
    restaurants_per_page = models.PositiveIntegerField(default=12, help_text="Restaurants shown per page")
    menu_items_per_page = models.PositiveIntegerField(default=20, help_text="Menu items shown per page")
    orders_per_page = models.PositiveIntegerField(default=10, help_text="Orders shown per page")
    show_out_of_stock = models.BooleanField(default=True, help_text="Show out-of-stock items")
    
    # Tax Settings
    enable_tax = models.BooleanField(default=False, help_text="Enable tax calculation")
    tax_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=7.50,
        help_text="Tax percentage to apply"
    )
    tax_name = models.CharField(max_length=50, default="VAT", help_text="Tax label (e.g., VAT, GST)")
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, default="We're currently performing maintenance. Please check back soon.")
    
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Platform Settings"
        verbose_name_plural = "Platform Settings"
    
    def save(self, *args, **kwargs):
        self.pk = 1  # Ensure singleton
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def __str__(self):
        return "Platform Settings"


# ============================================
# PROMO CODES SYSTEM
# ============================================
class PromoCode(models.Model):
    """Promotional discount codes"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage Off'),
        ('fixed', 'Fixed Amount Off'),
    ]
    
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Limits
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Maximum discount amount (for percentage discounts)"
    )
    usage_limit = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    usage_count = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=1, help_text="Times each user can use this code")
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Targeting
    all_restaurants = models.BooleanField(default=True)
    restaurants = models.ManyToManyField('restaurants.Restaurant', blank=True)
    first_order_only = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_promos')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_display()}"
    
    def get_discount_display(self):
        if self.discount_type == 'percentage':
            return f"{self.discount_value}% off"
        return f"₦{self.discount_value} off"
    
    def is_valid(self):
        """Check if promo code is currently valid"""
        now = timezone.now()
        if not self.is_active:
            return False, "This promo code is no longer active"
        if now < self.valid_from:
            return False, "This promo code is not yet valid"
        if self.valid_until and now > self.valid_until:
            return False, "This promo code has expired"
        if self.usage_limit > 0 and self.usage_count >= self.usage_limit:
            return False, "This promo code has reached its usage limit"
        return True, "Valid"
    
    def calculate_discount(self, order_total):
        """Calculate discount amount for an order total"""
        if order_total < self.minimum_order:
            return 0
        
        if self.discount_type == 'percentage':
            discount = (order_total * self.discount_value) / 100
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        else:
            discount = self.discount_value
        
        return min(discount, order_total)  # Don't exceed order total


class PromoCodeUsage(models.Model):
    """Track promo code usage by users"""
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-used_at']


# ============================================
# AUDIT LOG SYSTEM
# ============================================
class AuditLog(models.Model):
    """Track admin actions for security and compliance"""
    
    ACTION_TYPES = [
        ('user_create', 'User Created'),
        ('user_update', 'User Updated'),
        ('user_delete', 'User Deleted'),
        ('user_role_change', 'User Role Changed'),
        ('user_toggle', 'User Status Toggled'),
        ('restaurant_create', 'Restaurant Created'),
        ('restaurant_update', 'Restaurant Updated'),
        ('restaurant_delete', 'Restaurant Deleted'),
        ('restaurant_toggle', 'Restaurant Status Toggled'),
        ('order_update', 'Order Updated'),
        ('order_cancel', 'Order Cancelled'),
        ('promo_create', 'Promo Code Created'),
        ('promo_update', 'Promo Code Updated'),
        ('promo_delete', 'Promo Code Deleted'),
        ('settings_update', 'Settings Updated'),
        ('export_data', 'Data Exported'),
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('other', 'Other Action'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField()
    
    # Target entity
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Additional data
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_action_type_display()} - {self.created_at}"
    
    @classmethod
    def log(cls, user, action_type, description, target_model='', target_id=None, request=None, extra_data=None):
        """Helper method to create audit log entries"""
        log_entry = cls(
            user=user,
            action_type=action_type,
            description=description,
            target_model=target_model,
            target_id=target_id,
            extra_data=extra_data or {}
        )
        
        if request:
            log_entry.ip_address = cls.get_client_ip(request)
            log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        log_entry.save()
        return log_entry
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
