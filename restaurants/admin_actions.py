from django.core.management import call_command
from django.contrib import admin, messages
from .models import Restaurant


def add_buca_sample_menu(modeladmin, request, queryset):
    for restaurant in queryset:
        if 'buca republic' in restaurant.name.lower():
            call_command('sample_buca_menu')
            messages.success(request, f'Sample menu/categories added to {restaurant.name}.')
        else:
            messages.warning(request, f'Skipped {restaurant.name}: not Buca Republic.')
add_buca_sample_menu.short_description = "Add/refresh Buca Republic sample menu/categories"
