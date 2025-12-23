from django.contrib import admin
from django.contrib.auth.models import Group

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