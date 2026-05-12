from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import User, AddPropertyModel, PropertyLeadsModel, ProjectLeadsModel, ImagePost, Reels, ScheduledNotification, PropertyInteraction
from .services import NotificationService

@receiver(post_save, sender=User)
def handle_user_registration(sender, instance, created, **kwargs):
    if created:
        # 1. Immediate Welcome Email
        if instance.role == 'OWNER':
            tpl = NotificationService.get_template_content('REG_WELCOME_OWNER_1', {'user': instance})
            NotificationService.send_to_all(instance, tpl['subject'], tpl['body'])
            
            # Schedule 2nd and 3rd follow-ups
            ScheduledNotification.objects.create(
                user=instance,
                notification_type='REG_WELCOME_OWNER_2',
                scheduled_for=timezone.now() + timedelta(minutes=5)
            )
            ScheduledNotification.objects.create(
                user=instance,
                notification_type='REG_WELCOME_OWNER_3',
                scheduled_for=timezone.now() + timedelta(minutes=10)
            )
        else:
            # Check if has subscription (for now checking plan_type)
            event = 'REG_WELCOME_AGENT_HAS_SUB' if instance.plan_type else 'REG_WELCOME_AGENT_NO_SUB'
            tpl = NotificationService.get_template_content(event, {'user': instance})
            NotificationService.send_to_all(instance, tpl['subject'], tpl['body'])

@receiver(post_save, sender=AddPropertyModel)
def handle_property_status_change(sender, instance, created, **kwargs):
    if created:
        tpl = NotificationService.get_template_content('VERIFY_TECH_START')
        NotificationService.send_to_all(instance.user, tpl['subject'], tpl['body'])

@receiver(post_save, sender=PropertyLeadsModel)
def handle_property_lead(sender, instance, created, **kwargs):
    if created:
        owner = instance.leadTo
        tpl = NotificationService.get_template_content('LEAD_VIEW_PROP')
        NotificationService.send_to_all(owner, tpl['subject'], tpl['body'])

@receiver(post_save, sender=ImagePost)
def handle_news_feed_update(sender, instance, created, **kwargs):
    if created and instance.linked_property:
        viewers = PropertyInteraction.objects.filter(property=instance.linked_property).values_list('user', flat=True).distinct()
        for user_id in viewers:
            user = User.objects.get(id=user_id)
            tpl = NotificationService.get_template_content('UPDATE_NEWS_FEED', {'title': instance.heading})
            NotificationService.send_to_all(user, tpl['subject'], tpl['body'])

@receiver(post_save, sender=Reels)
def handle_property_byte_update(sender, instance, created, **kwargs):
    if created and instance.linked_property:
        viewers = PropertyInteraction.objects.filter(property=instance.linked_property).values_list('user', flat=True).distinct()
        for user_id in viewers:
            user = User.objects.get(id=user_id)
            ScheduledNotification.objects.create(
                user=user,
                notification_type='UPDATE_PROP_BYTE',
                scheduled_for=timezone.now() + timedelta(minutes=2),
                data={'title': instance.description}
            )
