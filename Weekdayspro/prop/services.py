import requests
from django.core.mail import send_mail
from django.conf import settings
from .models import NotificationLog

from django.template.loader import render_to_string
from django.utils.html import strip_tags

class NotificationService:
    @staticmethod
    def send_to_all(user, subject, message, template_id=None, context=None):
        """Sends notification through active channels."""
        # Phase 1: Email only for now
        NotificationService.send_email(user, subject, message, context)
        
        # Phase 2: WhatsApp (Wait for approval)
        # NotificationService.send_whatsapp(user.whatsapp_number or user.phone, message)

    @staticmethod
    def send_email(user, subject, body_text, context=None):
        try:
            # If we have a context, we can use a more professional HTML template later.
            # For now, we'll send the plain text body but structured for HTML.
            html_message = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
                <h2 style="color: #0d6efd;">{subject}</h2>
                <p>{body_text}</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #666;">
                    Sent by Weekdays Properties
                </p>
            </div>
            """
            
            send_mail(
                subject,
                body_text,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=html_message
            )
            NotificationLog.objects.create(user=user, channel="Email", notification_type=subject, success=True)
        except Exception as e:
            NotificationLog.objects.create(user=user, channel="Email", notification_type=subject, success=False, message=str(e))

    @staticmethod
    def get_template_content(event_type, context=None):
        """Returns subject and body based on handwriting notes."""
        user = context.get('user') if context else None
        
        templates = {
            'REG_WELCOME_OWNER_1': {
                'subject': 'Add your property',
                'body': 'Add your property to get buyers for your property.'
            },
            'REG_WELCOME_OWNER_2': {
                'subject': 'Get Rentals',
                'body': 'Add your property to get rentals.'
            },
            'REG_WELCOME_OWNER_3': {
                'subject': 'Explore Properties',
                'body': 'Explore Condetro to find a matching property for you.'
            },
            'REG_WELCOME_AGENT_NO_SUB': {
                'subject': 'Grow your business',
                'body': 'Get a subscription to promote your profile and property and get Leads, buyers.'
            },
            'REG_WELCOME_AGENT_HAS_SUB': {
                'subject': 'Engage with clients',
                'body': 'Add property, reels, and updates to engage with clients.'
            },
            'VERIFY_TECH_START': {
                'subject': 'Technical Verification',
                'body': 'Now your property is under technical verification.'
            },
            'VERIFY_TECH_DONE': {
                'subject': 'Technical Verification Completed',
                'body': 'Technical verification is successfully completed. Check details and confirm.'
            },
            'VERIFY_LEGAL_START': {
                'subject': 'Legal Verification',
                'body': "Thanks for confirming, now it's under legal verification."
            },
            'VERIFY_LEGAL_DONE': {
                'subject': 'Legal Verification Completed',
                'body': 'Legal verification is completed. Now we will find buyers for your property.'
            },
            'LEAD_VIEW_PROP': {
                'subject': 'Property Viewed',
                'body': "'Someone' viewed your property, he is interested in your property."
            },
            'LEAD_VIEW_PROFILE': {
                'subject': 'Profile Viewed',
                'body': f"'Someone' viewed your profile, he is looking for '{user.category if user else 'services'}' in '{user.location if user else 'your area'}'."
            },
            'UPDATE_NEWS_FEED': {
                'subject': 'Property Update',
                'body': f"A new update on the property that you showed interest in: {context.get('title') if context else ''}"
            },
            'UPDATE_PROP_BYTE': {
                'subject': 'New Property Byte',
                'body': "Watch property byte about the property you visited earlier."
            },
            'EDIT_ALERT': {
                'subject': 'Property Details Updated',
                'body': 'A property you previously visited has been updated with new details.'
            },
            'SITE_VISIT_OWNER': {
                'subject': 'Site Visit Scheduled',
                'body': 'A buyer is being sent to your property for a site visit.'
            }
        }
        return templates.get(event_type, {'subject': 'Notification', 'body': ''})

    @staticmethod
    def send_whatsapp(phone, message):
        """Placeholder for Phase 2."""
        print(f"PHASE 2 - WA: {phone}: {message}")
        return True

    @staticmethod
    def notify_visitors(instance, event_type):
        """Notifies all users who interacted with this property/project/profile."""
        from .models import PropertyInteraction, User
        
        # Get unique users who viewed this
        if hasattr(instance, 'projectName'): # Property
            viewers = PropertyInteraction.objects.filter(property=instance).values_list('user', flat=True).distinct()
        elif hasattr(instance, 'username'): # Profile
            # Need a model for profile views? We used 'click' count, but we should probably log interactions.
            # For now, let's assume we use a similar pattern if possible.
            viewers = [] 
        else:
            viewers = []

        tpl = NotificationService.get_template_content(event_type)
        for user_id in viewers:
            user = User.objects.get(id=user_id)
            if user != getattr(instance, 'user', None): # Don't notify the owner
                NotificationService.send_to_all(user, tpl['subject'], tpl['body'])
