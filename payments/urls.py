from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/verify/<str:reference>/', views.payment_verification, name='payment_verification'),
    path('payment/success/<str:reference>/', views.payment_success, name='payment_success'),
    path('payment/failed/<str:reference>/', views.payment_failed, name='payment_failed'),
    path('payment/history/', views.payment_history, name='payment_history'),
    path('ajax/history/payments/<slug:restaurant_slug>/', views.ajax_restaurant_payments, name='ajax_restaurant_payments'),
    path('payment/detail/<str:reference>/', views.payment_detail, name='payment_detail'),
    path('payment/retry/<str:reference>/', views.retry_payment, name='retry_payment'),
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]