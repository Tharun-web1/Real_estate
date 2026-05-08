from .models import Notification, ChatMessage
from django.db.models import Q

def notification_counts(request):
    if request.user.is_authenticated:
        # Unread notifications (matches, system, etc.)
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        # Unread messages count
        # We need to find messages sent by OTHERS in chats where the user is a participant
        unread_messages_count = ChatMessage.objects.filter(
            Q(chat__user1=request.user) | Q(chat__user2=request.user),
            is_read=False
        ).exclude(sender=request.user).count()
        
        total_notification_count = unread_notifications_count # or include messages? User said "show notification count" for notifications button and "aside bar messages show count"
        
        recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
        
        return {
            'unread_notifications_count': unread_notifications_count,
            'unread_messages_count': unread_messages_count,
            'total_notification_count': unread_notifications_count + unread_messages_count,
            'recent_notifications': recent_notifications
        }
    return {
        'unread_notifications_count': 0,
        'unread_messages_count': 0,
        'total_notification_count': 0
    }
