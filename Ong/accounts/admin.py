from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'phone_number')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('username', 'email', 'role', 'phone_number', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('Role & Permissions'), {
            'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'phone_number', 'password1', 'password2', 'is_verified', 'is_active', 'is_staff'),
        }),
    )
    
    actions = ['activate_users', 'deactivate_users', 'verify_users', 'make_admin', 'make_owner', 'make_customer']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated successfully.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated successfully.')
    deactivate_users.short_description = "Deactivate selected users"
    
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} users verified successfully.')
    verify_users.short_description = "Verify selected users"
    
    def make_admin(self, request, queryset):
        updated = queryset.update(role='admin')
        self.message_user(request, f'{updated} users set as Admin.')
    make_admin.short_description = "Set selected users as Admin"
    
    def make_owner(self, request, queryset):
        updated = queryset.update(role='restaurant_owner')
        self.message_user(request, f'{updated} users set as Restaurant Owner.')
    make_owner.short_description = "Set selected users as Restaurant Owner"
    
    def make_customer(self, request, queryset):
        updated = queryset.update(role='customer')
        self.message_user(request, f'{updated} users set as Customer.')
    make_customer.short_description = "Set selected users as Customer"