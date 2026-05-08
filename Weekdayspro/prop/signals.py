from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import User, AddPropertyModel, PropertyLeadsModel, ProjectLeadsModel, ImagePost, Reels, ScheduledNotification, PropertyInteraction
from .services import NotificationService

@receiver(post_save, sender=User)
def handle_user_registration(sender, instance, created, **kwargs):
    if created:
        # Schedule notification after 5 minutes
        ScheduledNotification.objects.create(
            user=instance,
            notification_type='REGISTRATION_FOLLOWUP',
            scheduled_for=timezone.now() + timedelta(minutes=5)
        )

@receiver(post_save, sender=AddPropertyModel)
def handle_property_status_change(sender, instance, created, **kwargs):
    if created:
        NotificationService.send_to_all(
            instance.user, 
            "Property Under Verification", 
            "Now your property is under technical verification."
        )
    # Verification updates would ideally track field changes. 
    # For this implementation, we assume these triggers are hit when the admin updates the flags.

@receiver(post_save, sender=PropertyLeadsModel)
def handle_property_lead(sender, instance, created, **kwargs):
    if created:
        owner = instance.leadTo
        if owner.role == 'OWNER':
             NotificationService.send_to_all(owner, "New Lead", "Someone is interested in your property.")
        else:
             NotificationService.send_to_all(owner, "New View", "Someone viewed your property, he is interested in your property.")

@receiver(post_save, sender=ImagePost)
def handle_news_feed_update(sender, instance, created, **kwargs):
    if created and instance.linked_property:
        # Find users who viewed this property
        viewers = PropertyInteraction.objects.filter(
            property=instance.linked_property
        ).values_list('user', flat=True).distinct()
        
        for user_id in viewers:
            user = User.objects.get(id=user_id)
            NotificationService.send_to_all(user, "Property Update", f"A new update on the property that you showed interest in: {instance.heading}")

@receiver(post_save, sender=Reels)
def handle_property_byte_update(sender, instance, created, **kwargs):
    if created and instance.linked_property:
        # Schedule after 2 minutes
        viewers = PropertyInteraction.objects.filter(
            property=instance.linked_property
        ).values_list('user', flat=True).distinct()
        
        for user_id in viewers:
            user = User.objects.get(id=user_id)
            ScheduledNotification.objects.create(
                user=user,
                notification_type='PROPERTY_BYTE_UPDATE',
                scheduled_for=timezone.now() + timedelta(minutes=2),
                data={'link': f"/reels/{instance.id}/", 'title': instance.description}
            )
