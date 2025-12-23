from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('pos', 'POS Terminal'),
        ('paystack', 'Paystack Online'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('awaiting_confirmation', 'Awaiting Confirmation'),
        ('success', 'Successful'),
        ('failed', 'Failed'),
        ('abandoned', 'Abandoned'),
    )
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    paystack_reference = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=25, choices=PAYMENT_METHOD_CHOICES, default='card')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    
    # Customer payment details
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=100)
    
    # Paystack response data
    gateway_response = models.TextField(blank=True)
    currency = models.CharField(max_length=3, default='NGN')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment #{self.reference} - {self.amount}"
    
    @property
    def is_successful(self):
        return self.status == 'success'