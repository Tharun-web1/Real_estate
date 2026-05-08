import requests
from django.core.mail import send_mail
from django.conf import settings
from .models import NotificationLog

class NotificationService:
    @staticmethod
    def send_to_all(user, subject, message, template_id=None):
        """Sends notification through all available channels."""
        # 1. Email
        NotificationService.send_email(user, subject, message)
        
        # 2. SMS (Dummy for now)
        NotificationService.send_sms(user.phone, template_id, {"message": message})
        
        # 3. WhatsApp (Dummy for now)
        NotificationService.send_whatsapp(user.whatsapp_number or user.phone, message)

    @staticmethod
    def send_email(user, subject, body):
        try:
            # For dummy testing, we can print to console if no email backend is configured
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            NotificationLog.objects.create(user=user, channel="Email", notification_type="Info", success=True)
        except Exception as e:
            NotificationLog.objects.create(user=user, channel="Email", notification_type="Info", success=False, message=str(e))

    @staticmethod
    def send_sms(phone, template_id, params):
        """Dummy SMS integration."""
        print(f"DEBUG: [SMS] Sending to {phone} using template {template_id}. Params: {params}")
        # In real scenario: requests.get(SMS_URL, params=...)
        return True

    @staticmethod
    def send_whatsapp(phone, message):
        """Dummy WhatsApp integration."""
        print(f"DEBUG: [WhatsApp] Sending to {phone}: {message}")
        # In real scenario: requests.post(WA_API_URL, json=...)
        return True
