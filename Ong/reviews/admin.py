from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
	list_display = ('id', 'restaurant', 'customer', 'rating', 'is_public', 'created_at')
	list_filter = ('restaurant', 'is_public', 'rating')
	search_fields = ('customer__username', 'comment')
	ordering = ('-created_at',)
