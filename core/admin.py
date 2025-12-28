
from django.contrib import admin
from django.contrib.auth.models import Group
from .models import AdminFeedback, PlatformSettings, PromoCode, PromoCodeUsage, AuditLog
# Register PlatformSettings with a custom admin class (singleton)
@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow editing the singleton
        return not PlatformSettings.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False
    list_display = ("site_name", "support_email", "commission_percentage", "currency", "updated_at")
    readonly_fields = ("updated_at", "updated_by")

# Register PromoCode with search, filters, and usage inline
class PromoCodeUsageInline(admin.TabularInline):
    model = PromoCodeUsage
    extra = 0
    readonly_fields = ("user", "order", "discount_amount", "used_at")

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "is_active", "valid_from", "valid_until", "usage_count")
    list_filter = ("discount_type", "is_active", "valid_from", "valid_until", "first_order_only")
    search_fields = ("code", "description")
    inlines = [PromoCodeUsageInline]
    readonly_fields = ("usage_count",)

@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ("promo_code", "user", "order", "discount_amount", "used_at")
    list_filter = ("promo_code", "user", "used_at")
    search_fields = ("promo_code__code", "user__username")
    readonly_fields = ("promo_code", "user", "order", "discount_amount", "used_at")

# Register AuditLog with filters and search
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action_type", "description", "target_model", "target_id", "created_at")
    list_filter = ("action_type", "user", "created_at")
    search_fields = ("description", "user__username", "target_model")
    readonly_fields = ("user", "action_type", "description", "target_model", "target_id", "ip_address", "user_agent", "extra_data", "created_at")

# Add a dashboard link to feedback (admin index)
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import messages

def feedback_link(modeladmin, request, queryset):
    url = reverse('admin:core_adminfeedback_changelist')
    messages.info(request, format_html('View all <a href="{}">Admin Feedback</a>.', url))

feedback_link.short_description = "Go to Admin Feedback list"

# Unregister default Group if not needed
admin.site.unregister(Group)

class CustomAdminSite(admin.AdminSite):
    site_header = "Restaurant SaaS Administration"
    site_title = "Restaurant SaaS Admin"
    index_title = "Welcome to Restaurant SaaS Platform Administration"

# Use the default admin site instead of replacing it
# admin.site = CustomAdminSite()  # REMOVE THIS LINE

# Just customize the existing admin site
admin.site.site_header = "Restaurant SaaS Administration"
admin.site.site_title = "Restaurant SaaS Admin"

admin.site.index_title = "Welcome to Restaurant SaaS Platform Administration"

# Register AdminFeedback with a custom admin class
@admin.register(AdminFeedback)
class AdminFeedbackAdmin(admin.ModelAdmin):
    list_display = ("subject", "sender", "sender_role", "created_at", "is_resolved")
    list_filter = ("sender_role", "is_resolved", "created_at")
    search_fields = ("subject", "message", "sender__username")
    readonly_fields = ("created_at",)
    actions = ["mark_as_resolved"]

    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True)
        self.message_user(request, f"{updated} feedback marked as resolved.")
    mark_as_resolved.short_description = "Mark selected feedback as resolved"