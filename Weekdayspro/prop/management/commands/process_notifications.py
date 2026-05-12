import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from prop.models import ScheduledNotification, AddPropertyModel
from prop.services import NotificationService

class Command(BaseCommand):
    help = 'Processes scheduled notifications'

    def handle(self, *args, **options):
        self.stdout.write("Starting notification worker...")
        while True:
            now = timezone.now()
            pending = ScheduledNotification.objects.filter(
                scheduled_for__lte=now,
                sent=False
            )

            for sn in pending:
                try:
                    self.process_notification(sn)
                    sn.sent = True
                    sn.save()
                    self.stdout.write(f"Sent {sn.notification_type} to {sn.user.username}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error sending {sn.id}: {str(e)}"))

            time.sleep(30) # Check every 30 seconds

    def process_notification(self, sn):
        user = sn.user
        
        # Check if the notification type exists in our template system
        tpl = NotificationService.get_template_content(sn.notification_type, {'user': user, 'title': sn.data.get('title')})
        
        if tpl['body']:
            NotificationService.send_to_all(user, tpl['subject'], tpl['body'])
        else:
            # Fallback for old types if any
            if sn.notification_type == 'REGISTRATION_FOLLOWUP':
                 if user.role == 'OWNER':
                # Check if they added a property
                if not AddPropertyModel.objects.filter(user=user).exists():
                    NotificationService.send_to_all(user, "Get Started", "Add your property to get buyers for your property.")
                 else:
                    NotificationService.send_to_all(user, "Explore", "Explore Condetro to find a matching property for you.")
            
            elif user.role in ['MARKETER', 'COMPANY', 'PROFESSIONAL']:
                # Agent follow-up
                if not user.plan_type:
                    NotificationService.send_to_all(user, "Grow your business", "Get a subscription to promote your profile and properties.")
                else:
                    NotificationService.send_to_all(user, "Engagement", "Add property, reel or updates to engage with clients.")

        elif sn.notification_type == 'PROPERTY_BYTE_UPDATE':
             NotificationService.send_to_all(user, "New Property Byte", f"Watch property byte about the property you visited earlier: {sn.data.get('title')}")
