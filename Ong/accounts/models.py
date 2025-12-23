from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('restaurant_owner', 'Restaurant Owner'),
        ('customer', 'Customer'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Preferred Restaurant (for direct access feature)
    preferred_restaurant = models.ForeignKey(
        'restaurants.Restaurant', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='preferred_customers',
        help_text='Customer\'s default/preferred restaurant for direct access'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Add related_name to avoid clashes with default User model
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='customuser_set',  # ADD THIS
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',  # ADD THIS
        related_query_name='user',
    )

    def __str__(self):
        return f"{self.username} ({self.role})"