from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from orders.models import Order, Review
from restaurants.models import Restaurant
from django.db import models
from .models import Feedback
from django.views.decorators.http import require_POST
from django.urls import reverse


@login_required
def owner_feedback_moderation(request, restaurant_id):
    """Restaurant owner view to moderate feedback for their restaurant."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.user.role != 'restaurant_owner' or restaurant.owner != request.user:
        if not request.user.is_staff:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')

    feedback_qs = Feedback.objects.filter(restaurant=restaurant).order_by('-created_at')

    context = {
        'restaurant': restaurant,
        'feedback_list': feedback_qs,
    }
    return render(request, 'reviews/feedback_moderation.html', context)


@login_required
@require_POST
def approve_feedback(request, feedback_id):
    """Approve or unapprove a feedback entry (toggle)."""
    fb = get_object_or_404(Feedback, id=feedback_id)
    restaurant = fb.restaurant
    # only restaurant owner or staff can approve
    if request.user.role != 'restaurant_owner' or restaurant.owner != request.user:
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Access denied.'}, status=403)

    action = request.POST.get('action', 'approve')
    if action == 'approve':
        fb.is_public = True
    else:
        fb.is_public = False
    fb.save()

    return JsonResponse({'success': True, 'id': fb.id, 'is_public': fb.is_public})

@login_required
def submit_review(request, order_id):
    """Submit a review for a completed order"""
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can submit reviews.')
        return redirect('dashboard')
    
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Check if order is completed
    if order.status != 'completed':
        messages.error(request, 'You can only review completed orders.')
        return redirect('order_detail', order_id=order_id)
    
    # Check if review already exists
    if hasattr(order, 'review'):
        messages.info(request, 'You have already reviewed this order.')
        return redirect('order_detail', order_id=order_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        review = Review.objects.create(
            order=order,
            customer=request.user,
            restaurant=order.restaurant,
            rating=rating,
            comment=comment
        )
        
        messages.success(request, 'Thank you for your review!')
        return redirect('order_detail', order_id=order_id)
    
    context = {
        'order': order,
    }
    return render(request, 'reviews/submit_review.html', context)

@login_required
def restaurant_reviews(request, restaurant_id):
    """View all reviews for a restaurant"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check if user owns the restaurant or is admin
    if request.user.role != 'restaurant_owner' or restaurant.owner != request.user:
        if not request.user.is_staff:
            messages.error(request, 'Access denied.')
            return redirect('dashboard')
    
    reviews = Review.objects.filter(restaurant=restaurant, is_approved=True)
    
    # Calculate average rating
    avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
    total_reviews = reviews.count()
    
    # Rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()
    
    context = {
        'restaurant': restaurant,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'rating_distribution': rating_distribution,
    }
    return render(request, 'reviews/restaurant_reviews.html', context)


@login_required
@require_POST
def submit_feedback(request, slug):
    """Submit general feedback for a restaurant (not order-bound)."""
    restaurant = get_object_or_404(Restaurant, slug=slug, is_active=True)

    # Only customers may submit feedback when logged in; allow anonymous if not authenticated
    rating = int(request.POST.get('rating', 5))
    comment = request.POST.get('comment', '').strip()

    fb = Feedback.objects.create(
        customer=request.user if request.user.is_authenticated and request.user.role == 'customer' else None,
        restaurant=restaurant,
        rating=rating,
        comment=comment,
        is_public=True
    )

    # If AJAX, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'id': fb.id,
            'rating': fb.rating,
            'comment': fb.comment,
            'created_at': fb.created_at.strftime('%Y-%m-%d %H:%M')
        })

    messages.success(request, 'Thank you for your feedback!')
    return redirect('restaurant_detail', slug=slug)