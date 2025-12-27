
from django.urls import path
from . import views
from .views_load_restaurants import load_restaurants

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    # TEMP: Load restaurants.json into DB (superuser only)
    path('admin/load-restaurants/', load_restaurants, name='load_restaurants'),
    path('admin-dashboard/', views.dashboard, name='admin_dashboard'),  # Alias for admin notifications
    
    # Public pages
    path('', views.home, name='home'),
    path('browse/', views.browse_restaurants, name='browse_restaurants'),
    
    # RESTAURANT MANAGEMENT URLs (Owner only) - ADD THIS MISSING URL!
    path('restaurants/add/', views.add_restaurant, name='add_restaurant'),
    path('restaurants/<int:restaurant_id>/edit/', views.edit_restaurant, name='edit_restaurant'),
    path('restaurants/<int:restaurant_id>/delete/', views.delete_restaurant, name='delete_restaurant'),
    path('restaurants/<int:restaurant_id>/menu/', views.manage_menu, name='manage_menu'),
    
    # ORDER MANAGEMENT URLs
    path('orders/', views.order_management, name='order_management'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    
    # Analytics, Settings, Notifications
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('settings/', views.settings_dashboard, name='settings_dashboard'),
    path('notifications/', views.notifications_dashboard, name='notifications_dashboard'),
    
    # ADMIN USER MANAGEMENT URLs
    path('admin/users/<int:user_id>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin/users/<int:user_id>/change-role/', views.admin_change_user_role, name='admin_change_user_role'),
    path('admin/users/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/restaurants/<int:restaurant_id>/toggle/', views.admin_toggle_restaurant, name='admin_toggle_restaurant'),
    path('admin/restaurants/<int:restaurant_id>/delete/', views.admin_delete_restaurant, name='admin_delete_restaurant'),
    
    # PROMO CODE MANAGEMENT URLs
    path('admin/promo-codes/', views.promo_code_list, name='promo_code_list'),
    path('admin/promo-codes/create/', views.promo_code_create, name='promo_code_create'),
    path('admin/promo-codes/<int:promo_id>/toggle/', views.promo_code_toggle, name='promo_code_toggle'),
    path('admin/promo-codes/<int:promo_id>/delete/', views.promo_code_delete, name='promo_code_delete'),
    path('api/validate-promo/', views.validate_promo_code, name='validate_promo_code'),
    
    # EXPORT URLs
    path('admin/export/users/', views.export_users, name='export_users'),
    path('admin/export/restaurants/', views.export_restaurants, name='export_restaurants'),
    path('admin/export/orders/', views.export_orders, name='export_orders'),
    path('admin/export/revenue/', views.export_revenue_report, name='export_revenue_report'),
    
    # AUDIT LOG URLs
    path('admin/audit-logs/', views.audit_log_list, name='audit_log_list'),
]