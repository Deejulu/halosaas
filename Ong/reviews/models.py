from django.db import models
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant

User = get_user_model()

# General feedback submitted by customers (not necessarily tied to an order)
class Feedback(models.Model):
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
	rating = models.PositiveSmallIntegerField(default=5)
	comment = models.TextField(blank=True)
	# By default feedback is not public until approved by owner/admin
	is_public = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		who = self.customer.username if self.customer else 'Anonymous'
		return f"Feedback by {who} @ {self.restaurant.name}"
