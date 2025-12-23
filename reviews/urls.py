from django.urls import path
from . import views

urlpatterns = [
    path('order/<int:order_id>/review/', views.submit_review, name='submit_review'),
    path('restaurant/<int:restaurant_id>/reviews/', views.restaurant_reviews, name='restaurant_reviews'),
    path('restaurant/<slug:slug>/feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('restaurant/<int:restaurant_id>/feedback/moderation/', views.owner_feedback_moderation, name='feedback_moderation'),
    path('feedback/<int:feedback_id>/approve/', views.approve_feedback, name='approve_feedback'),
]