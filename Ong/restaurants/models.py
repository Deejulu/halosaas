from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'restaurant_owner'})
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='restaurant_banners/', blank=True, null=True)
    
    # Restaurant hours
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    
    # Hero Section Customization
    hero_title = models.CharField(max_length=200, blank=True, default="")
    hero_subtitle = models.TextField(blank=True, default="")
    hero_image = models.ImageField(upload_to='restaurant_hero/', blank=True, null=True)
    
    # About Section
    about_title = models.CharField(max_length=200, blank=True, default="Our Story")
    about_content = models.TextField(blank=True, default="")
    chef_name = models.CharField(max_length=100, blank=True, default="")
    chef_bio = models.TextField(blank=True, default="")
    chef_image = models.ImageField(upload_to='chef_images/', blank=True, null=True)
    
    # Contact & Social
    website = models.URLField(blank=True, default="")
    facebook = models.URLField(blank=True, default="")
    instagram = models.URLField(blank=True, default="")
    twitter = models.URLField(blank=True, default="")
    
    # Payment Methods
    accepts_cash = models.BooleanField(default=True, help_text="Accept cash payments")
    accepts_card = models.BooleanField(default=False, help_text="Accept card payments (Visa, Mastercard)")
    accepts_bank_transfer = models.BooleanField(default=False, help_text="Accept bank transfers")
    accepts_mobile_money = models.BooleanField(default=False, help_text="Accept mobile money (MTN, Airtel, etc.)")
    accepts_paystack = models.BooleanField(default=False, help_text="Accept Paystack online payments")
    accepts_pos = models.BooleanField(default=False, help_text="Accept POS terminal payments")
    bank_name = models.CharField(max_length=100, blank=True, default="")
    bank_account_number = models.CharField(max_length=20, blank=True, default="")
    bank_account_name = models.CharField(max_length=100, blank=True, default="")
    mobile_money_number = models.CharField(max_length=20, blank=True, default="")
    mobile_money_provider = models.CharField(max_length=50, blank=True, default="")
    
    # ==================== THEME & APPEARANCE ====================
    
    # Template Style
    TEMPLATE_CHOICES = [
        ('classic', 'Classic'),
        ('modern', 'Modern'),
        ('minimal', 'Minimal'),
        ('elegant', 'Elegant'),
        ('fastfood', 'Fast Food'),
    ]
    template_style = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='classic')
    
    # Font Style
    FONT_CHOICES = [
        ('default', 'Default (System)'),
        ('modern', 'Modern (Poppins)'),
        ('classic', 'Classic (Playfair Display)'),
        ('playful', 'Playful (Fredoka)'),
        ('elegant', 'Elegant (Cormorant Garamond)'),
        ('bold', 'Bold (Montserrat)'),
    ]
    font_style = models.CharField(max_length=20, choices=FONT_CHOICES, default='default')
    
    # Header Style
    HEADER_CHOICES = [
        ('full_banner', 'Full Banner'),
        ('compact', 'Compact Header'),
        ('split', 'Split Layout'),
        ('video', 'Video Background'),
        ('slideshow', 'Image Slideshow'),
    ]
    header_style = models.CharField(max_length=20, choices=HEADER_CHOICES, default='full_banner')
    header_video = models.FileField(upload_to='restaurant_videos/', blank=True, null=True)
    
    # Menu Layout
    MENU_LAYOUT_CHOICES = [
        ('grid', 'Grid Cards'),
        ('list', 'List View'),
        ('gallery', 'Image Gallery'),
        ('compact', 'Compact List'),
        ('magazine', 'Magazine Style'),
    ]
    menu_layout = models.CharField(max_length=20, choices=MENU_LAYOUT_CHOICES, default='grid')
    
    # Button Style
    BUTTON_STYLE_CHOICES = [
        ('rounded', 'Rounded'),
        ('sharp', 'Sharp Corners'),
        ('pill', 'Pill Shape'),
        ('outline', 'Outline Only'),
        ('gradient', 'Gradient'),
    ]
    button_style = models.CharField(max_length=20, choices=BUTTON_STYLE_CHOICES, default='rounded')
    
    # Colors (Extended)
    primary_color = models.CharField(max_length=7, blank=True, default="#007bff")
    secondary_color = models.CharField(max_length=7, blank=True, default="#6c757d")
    accent_color = models.CharField(max_length=7, blank=True, default="#28a745")
    text_color = models.CharField(max_length=7, blank=True, default="#333333")
    background_color = models.CharField(max_length=7, blank=True, default="#ffffff")
    header_bg_color = models.CharField(max_length=7, blank=True, default="#000000")
    header_text_color = models.CharField(max_length=7, blank=True, default="#ffffff")
    
    # Section Visibility
    show_hero = models.BooleanField(default=True, help_text="Show hero/banner section")
    show_about = models.BooleanField(default=True, help_text="Show about section")
    show_gallery = models.BooleanField(default=True, help_text="Show gallery section")
    show_reviews = models.BooleanField(default=True, help_text="Show reviews section")
    show_contact = models.BooleanField(default=True, help_text="Show contact section")
    show_social = models.BooleanField(default=True, help_text="Show social media links")
    show_chef = models.BooleanField(default=False, help_text="Show chef information")
    show_hours = models.BooleanField(default=True, help_text="Show opening hours")
    
    # Advanced Customization
    custom_css = models.TextField(blank=True, default="", help_text="Custom CSS for advanced styling")
    
    # ==================== END THEME ====================
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class GalleryImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='restaurant_gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-id']
    
    def __str__(self):
        return f"Gallery image for {self.restaurant.name}"

class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.PositiveIntegerField(help_text="Preparation time in minutes", default=15)
    
    # Stock/Inventory tracking
    track_stock = models.BooleanField(default=False, help_text="Enable stock tracking for this item")
    stock_quantity = models.PositiveIntegerField(default=0, help_text="Number of portions available")
    low_stock_threshold = models.PositiveIntegerField(default=5, help_text="Alert when stock falls below this")
    
    # Disable reason tracking
    DISABLE_REASONS = [
        ('', 'No reason'),
        ('sold_out', 'Sold Out'),
        ('seasonal', 'Seasonal Item'),
        ('ingredients', 'Missing Ingredients'),
        ('maintenance', 'Under Maintenance'),
        ('discontinued', 'Discontinued'),
        ('other', 'Other'),
    ]
    disabled_reason = models.CharField(max_length=50, blank=True, default='', choices=DISABLE_REASONS)
    disabled_reason_note = models.CharField(max_length=200, blank=True, default='')
    disabled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name
    
    @property
    def availability_status(self):
        """
        Returns a tuple of (status_code, display_text, css_class)
        
        Status codes:
        - 'in_stock': Stock tracking ON, quantity > low threshold
        - 'low_stock': Stock tracking ON, quantity > 0 but <= threshold
        - 'out_of_stock': Stock tracking ON, quantity = 0
        - 'available': Stock tracking OFF, manually enabled
        - 'unavailable': Stock tracking OFF, manually disabled
        """
        if self.track_stock:
            if self.stock_quantity == 0:
                return ('out_of_stock', 'Out of Stock', 'bg-danger')
            elif self.stock_quantity <= self.low_stock_threshold:
                return ('low_stock', f'Low Stock ({self.stock_quantity})', 'bg-warning text-dark')
            else:
                return ('in_stock', f'In Stock ({self.stock_quantity})', 'bg-success')
        else:
            if self.is_available:
                return ('available', 'Available', 'bg-success')
            else:
                return ('unavailable', 'Unavailable', 'bg-danger')
    
    @property
    def can_be_ordered(self):
        """Check if this item can be added to cart/ordered"""
        if self.track_stock:
            return self.stock_quantity > 0
        return self.is_available
    
    def reduce_stock(self, quantity=1):
        """Reduce stock after an order"""
        if self.track_stock and self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            if self.stock_quantity == 0:
                self.is_available = False
            self.save()
            return True
        return False
    
    def add_stock(self, quantity):
        """Add stock (restock)"""
        if self.track_stock:
            self.stock_quantity += quantity
            if self.stock_quantity > 0 and not self.is_available:
                self.is_available = True
            self.save()


class Staff(models.Model):
    """Staff members for a restaurant with role-based permissions"""
    
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('kitchen', 'Kitchen Staff'),
        ('waiter', 'Waiter/Server'),
    ]
    
    # Permission definitions for each role
    ROLE_PERMISSIONS = {
        'manager': {
            'can_view_orders': True,
            'can_update_order_status': True,
            'can_confirm_payment': True,
            'can_manage_menu': True,
            'can_view_reports': True,
            'can_manage_staff': True,
            'can_view_customers': True,
            'can_handle_refunds': True,
        },
        'cashier': {
            'can_view_orders': True,
            'can_update_order_status': False,
            'can_confirm_payment': True,
            'can_manage_menu': False,
            'can_view_reports': False,
            'can_manage_staff': False,
            'can_view_customers': True,
            'can_handle_refunds': False,
        },
        'kitchen': {
            'can_view_orders': True,
            'can_update_order_status': True,  # Only preparing -> ready
            'can_confirm_payment': False,
            'can_manage_menu': False,
            'can_view_reports': False,
            'can_manage_staff': False,
            'can_view_customers': False,
            'can_handle_refunds': False,
        },
        'waiter': {
            'can_view_orders': True,
            'can_update_order_status': True,  # Only ready -> delivered
            'can_confirm_payment': True,  # Can mark cash received
            'can_manage_menu': False,
            'can_view_reports': False,
            'can_manage_staff': False,
            'can_view_customers': True,
            'can_handle_refunds': False,
        },
    }
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_roles')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='staff_members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # Employment details
    employee_id = models.CharField(max_length=20, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    
    # Status
    is_active = models.BooleanField(default=True)
    hired_date = models.DateField(auto_now_add=True)
    
    # Invite tracking
    invite_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    invite_accepted = models.BooleanField(default=False)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_invited')
    invited_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Staff"
        unique_together = ['user', 'restaurant']
        ordering = ['restaurant', 'role', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()} at {self.restaurant.name}"
    
    def has_permission(self, permission):
        """Check if staff has a specific permission based on their role"""
        role_perms = self.ROLE_PERMISSIONS.get(self.role, {})
        return role_perms.get(permission, False)
    
    @property
    def permissions(self):
        """Get all permissions for this staff member"""
        return self.ROLE_PERMISSIONS.get(self.role, {})
    
    @classmethod
    def generate_invite_code(cls):
        """Generate a unique invite code"""
        import uuid
        return str(uuid.uuid4())[:12].upper()
    
    @classmethod
    def get_staff_for_user(cls, user, restaurant=None):
        """Get staff record for a user, optionally filtered by restaurant"""
        queryset = cls.objects.filter(user=user, is_active=True)
        if restaurant:
            queryset = queryset.filter(restaurant=restaurant)
        return queryset.first()


class StaffInvite(models.Model):
    """Track pending staff invitations"""
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='staff_invites')
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=Staff.ROLE_CHOICES)
    invite_code = models.CharField(max_length=50, unique=True)
    
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    invited_at = models.DateTimeField(auto_now_add=True)
    
    is_accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_invites')
    
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-invited_at']
    
    def __str__(self):
        return f"Invite for {self.email} as {self.get_role_display()} at {self.restaurant.name}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_accepted and not self.is_expired