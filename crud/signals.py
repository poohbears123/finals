from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import logging
from .models import Purchase
from .utils import send_to_zapier

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Purchase)
def cache_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Purchase.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Purchase.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Purchase)
def notify_status_change(sender, instance, created, **kwargs):
    if not created:
        old_status = getattr(instance, '_old_status', None)
        if old_status != instance.status:
            # Flatten payload to avoid nested structures for Zapier
            payload = {
                'user': str(instance.user.username),
                'email': str(instance.user.email),
                'item_name': str(instance.item.name),
                'quantity': str(instance.quantity),
                'status': str(instance.status),
                'message': f'Your product status is {instance.status}.',
            }
            logger.info(f"Sending payload to Zapier: {payload}")
            result = send_to_zapier(payload)
            if not result:
                logger.error("Failed to send payload to Zapier")
