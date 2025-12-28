from django.urls import path
from . import views

urlpatterns = [
    # Order URLs
    path('order/<slug:restaurant_slug>/', views.create_order, name='create_order'),
    path('history/', views.order_history, name='order_history'),
    path('ajax/history/orders/<slug:restaurant_slug>/', views.ajax_restaurant_orders, name='ajax_restaurant_orders'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('<int:order_id>/confirm-payment/', views.confirm_payment, name='confirm_payment'),
    path('<int:order_id>/reject-payment/', views.reject_payment, name='reject_payment'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('<int:order_id>/delivery-method/', views.choose_delivery_method, name='choose_delivery_method'),
    
    # Cart URLs
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/ajax/summary/', views.ajax_cart_summary, name='ajax_cart_summary'),
    path('cart/ajax/total_count/', views.ajax_cart_total_count, name='ajax_cart_total_count'),
    path('cart/switch/<int:restaurant_id>/', views.switch_cart_restaurant, name='switch_cart_restaurant'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_checkout, name='process_checkout'),
]