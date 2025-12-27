from django.contrib import admin
from .models import Restaurant, Category, MenuItem, GalleryImage
from restaurants.management.commands.populate_sample_menus import SAMPLE_MENUS
from .admin_actions import add_buca_sample_menu

class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1
    fields = ('image', 'caption', 'order')

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ('name', 'price', 'is_available', 'preparation_time')

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1
    fields = ('name', 'description', 'order')

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'phone', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username', 'phone', 'email', 'address')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [GalleryImageInline, CategoryInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'slug', 'description', 'logo', 'banner_image')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        ('Business Hours', {
            'fields': ('opening_time', 'closing_time')
        }),
        ('Customization', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_image', 'about_title', 'about_content')
        }),
        ('Social Media', {
            'fields': ('facebook', 'instagram', 'twitter')
        }),
        ('Theme & Design', {
            'fields': ('primary_color', 'secondary_color', 'chef_name', 'chef_bio', 'chef_image')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    prepopulated_fields = {'slug': ('name',)}
    actions = ['activate_restaurants', 'deactivate_restaurants', 'populate_menu', 'add_buca_sample_menu']
    
    def activate_restaurants(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} restaurants activated successfully.')
    activate_restaurants.short_description = "Activate selected restaurants"
    
    def deactivate_restaurants(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} restaurants deactivated successfully.')
    deactivate_restaurants.short_description = "Deactivate selected restaurants"
    
    def populate_menu(self, request, queryset):
        import traceback, logging
        logger = logging.getLogger("django")
        total_items = 0
        try:
            for restaurant in queryset:
                menu_def = SAMPLE_MENUS.get(restaurant.name)
                if not menu_def:
                    self.message_user(request, f"No structured menu for {restaurant.name}, skipping.", level='warning')
                    continue
                for cat_def in menu_def:
                    cat_name = cat_def.get('category', 'Main Dishes')
                    cat_desc = cat_def.get('description', '')
                    category, _ = Category.objects.get_or_create(
                        restaurant=restaurant,
                        name=cat_name,
                        defaults={'description': cat_desc}
                    )
                    for item in cat_def.get('items', []):
                        try:
                            MenuItem.objects.get_or_create(
                                category=category,
                                name=item['name'],
                                defaults={
                                    'description': item.get('description', ''),
                                    'price': item.get('price', 0),
                                    'is_available': True,
                                    'preparation_time': item.get('prep_time', 10),
                                }
                            )
                            total_items += 1
                        except Exception as e:
                            logger.error(f"Error creating menu item for {restaurant.name}: {item.get('name', 'UNKNOWN')}")
                            logger.error(traceback.format_exc())
                            self.message_user(request, f"Error creating menu item: {item.get('name', 'UNKNOWN')} ({e})", level='error')
            self.message_user(request, f'Menu populated successfully! Added {total_items} items across {queryset.count()} restaurants.')
        except Exception as e:
            logger.error("Error in populate_menu admin action:")
            logger.error(traceback.format_exc())
            self.message_user(request, f"Error populating menu: {e}", level='error')
    populate_menu.short_description = "Populate menu with sample items"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'order', 'menu_item_count')
    list_filter = ('restaurant',)
    search_fields = ('name', 'restaurant__name')
    list_editable = ('order',)
    
    def menu_item_count(self, obj):
        return obj.menuitem_set.count()
    menu_item_count.short_description = 'Menu Items'

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'restaurant', 'price', 'is_available', 'preparation_time')
    list_filter = ('is_available', 'category__restaurant', 'category')
    search_fields = ('name', 'category__name', 'category__restaurant__name')
    list_editable = ('price', 'is_available', 'preparation_time')
    
    def restaurant(self, obj):
        return obj.category.restaurant
    restaurant.short_description = 'Restaurant'
    
    actions = ['make_available', 'make_unavailable']
    
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} menu items made available.')
    make_available.short_description = "Make selected items available"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} menu items made unavailable.')
    make_unavailable.short_description = "Make selected items unavailable"

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'caption', 'order')
    list_filter = ('restaurant',)
    search_fields = ('caption', 'restaurant__name')
    list_editable = ('order',)