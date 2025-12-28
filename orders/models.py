from django.db import models
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant, MenuItem

User = get_user_model()

class Order(models.Model):
    DELIVERY_METHOD_CHOICES = (
        ('pickup', 'Pick Up'),
        ('delivery', 'Delivery'),
        ('', 'Not Specified'),
    )

    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES, default='', blank=True)
    delivery_info = models.JSONField(blank=True, null=True, help_text='Extra info for delivery orders (name, phone, email, WhatsApp)')
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('awaiting_confirmation', 'Awaiting Payment Confirmation'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash on Delivery'),
        ('card', 'Card (Paystack)'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('pos', 'POS Terminal'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('awaiting_confirmation', 'Awaiting Confirmation'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    )
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'customer'})
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_instructions = models.TextField(blank=True)
    
    # Payment tracking
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_reference = models.CharField(max_length=100, blank=True, default='')
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True, help_text='Upload proof of payment for bank transfers')
    
    # Customer details for the order
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.restaurant.name}"

    def calculate_total(self):
        return sum(item.total_price for item in self.orderitem_set.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    special_requests = models.TextField(blank=True)

    @property
    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"


# Persistent Cart Model for Admin Visibility
class SavedCart(models.Model):
    """Persistent cart stored in database for admin tracking"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_carts')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['customer', 'restaurant']
    
    def __str__(self):
        return f"Cart: {self.customer.username} @ {self.restaurant.name}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class SavedCartItem(models.Model):
    """Item in a saved cart"""
    cart = models.ForeignKey(SavedCart, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'menu_item']
    
    @property
    def total_price(self):
        return self.menu_item.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"


# Add this to the bottom of orders/models.py
class Review(models.Model):
    RATING_CHOICES = (
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'customer'})
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['order', 'customer']
    
    def __str__(self):
        return f"Review for {self.restaurant.name} by {self.customer.username}"
    
    def get_rating_stars(self):
        return '⭐' * self.rating   