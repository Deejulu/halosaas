from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def ensure_status_matches_payment(sender, instance, **kwargs):
    """Ensure order.status is consistent with payment_status after save."""
    if instance.payment_status == 'confirmed' and instance.status in ['pending', 'awaiting_confirmation', 'confirmed']:
        instance.status = 'completed'
        instance.save()
