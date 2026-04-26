# signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Product, PriceHistory

@receiver(pre_save, sender=Product)
def track_price_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = Product.objects.get(pk=instance.pk)
    if old.price_per_ton != instance.price_per_ton:
        PriceHistory.objects.create(
            product=instance,
            old_price=old.price_per_ton,
            new_price=instance.price_per_ton,
            note='Auto update'
        )