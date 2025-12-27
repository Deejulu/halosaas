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
    
    # Security Questions for Account Recovery
    SECURITY_QUESTIONS = (
        ('birth_city', 'What city were you born in?'),
        ('first_school', 'What was the name of your first school?'),
        ('favorite_color', 'What is your favorite color?'),
        ('mothers_maiden', "What is your mother's maiden name?"),
        ('first_pet', 'What was the name of your first pet?'),
    )
    
    security_question1 = models.CharField(
        max_length=20, 
        choices=SECURITY_QUESTIONS, 
        blank=True, 
        null=True,
        help_text='First security question for account recovery'
    )
    security_answer1 = models.CharField(
        max_length=100, 
        blank=True, 
        help_text='Answer to first security question'
    )
    
    security_question2 = models.CharField(
        max_length=20, 
        choices=SECURITY_QUESTIONS, 
        blank=True, 
        null=True,
        help_text='Second security question for account recovery'
    )
    security_answer2 = models.CharField(
        max_length=100, 
        blank=True, 
        help_text='Answer to second security question'
    )
    
    security_question3 = models.CharField(
        max_length=20, 
        choices=SECURITY_QUESTIONS, 
        blank=True, 
        null=True,
        help_text='Third security question for account recovery'
    )
    security_answer3 = models.CharField(
        max_length=100, 
        blank=True, 
        help_text='Answer to third security question'
    )

    # Preferred restaurant (customer feature)
    preferred_restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_by_users',
        help_text='Customer preferred restaurant for quick access'
    )

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