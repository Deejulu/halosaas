from django.core.management.base import BaseCommand
from orders.models import Order


class Command(BaseCommand):
    help = 'Reconcile orders: if payment_status is confirmed and order.status is pending/awaiting_confirmation, set status to confirmed'

    def handle(self, *args, **options):
        qs = Order.objects.filter(payment_status='confirmed', status__in=['pending', 'awaiting_confirmation'])
        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No orders to reconcile.'))
            return
        for o in qs:
            old = o.status
            o.status = 'confirmed'
            o.save()
            self.stdout.write(f'Updated Order #{o.id}: {old} -> confirmed')

        self.stdout.write(self.style.SUCCESS(f'Reconciled {count} orders.'))
