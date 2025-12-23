from django.urls import path
from . import views

urlpatterns = [
    # Restaurant Dashboard
    path('dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    
    # Restaurant Management
    path('manage/', views.manage_restaurant, name='manage_restaurant'),
    path('manage/<int:restaurant_id>/', views.manage_restaurant, name='manage_restaurant'),
    path('<int:restaurant_id>/menu/', views.manage_menu, name='manage_menu'),
    path('<int:restaurant_id>/orders/', views.restaurant_orders, name='restaurant_orders'),
    
    # AJAX endpoints - MENU MANAGEMENT
    path('<int:restaurant_id>/add-category/', views.add_category, name='add_category'),
    path('category/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('<int:restaurant_id>/category/<int:category_id>/add-item/', views.add_menu_item, name='add_menu_item'),
    path('menu-item/<int:item_id>/edit/', views.edit_menu_item, name='edit_menu_item'),
    path('menu-item/<int:item_id>/delete/', views.delete_menu_item, name='delete_menu_item'),
    path('menu-item/<int:item_id>/toggle/', views.toggle_menu_item, name='toggle_menu_item'),
    path('menu-item/<int:item_id>/update-stock/', views.update_stock, name='update_stock'),
    path('order/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('<int:restaurant_id>/bulk-update-order-status/', views.bulk_update_order_status, name='bulk_update_order_status'),
    
    # Staff Management
    path('<slug:slug>/staff/', views.manage_staff, name='manage_staff'),
    path('<slug:slug>/staff/invite/', views.invite_staff, name='invite_staff'),
    path('<slug:slug>/staff/<int:staff_id>/update/', views.update_staff, name='update_staff'),
    path('<slug:slug>/staff/invite/<int:invite_id>/cancel/', views.cancel_invite, name='cancel_invite'),
    path('<slug:slug>/staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('<slug:slug>/staff/order/<int:order_id>/', views.staff_update_order, name='staff_update_order'),
    
    # Preferred Restaurant (Customer Feature)
    path('<slug:slug>/set-preferred/', views.set_preferred_restaurant, name='set_preferred_restaurant'),
    path('remove-preferred/', views.remove_preferred_restaurant, name='remove_preferred_restaurant'),
    
    # Public restaurant page - KEEP LAST!
    path('<slug:slug>/', views.restaurant_detail, name='restaurant_detail'),
]