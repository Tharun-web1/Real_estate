from django.utils import timezone
from datetime import timedelta

class OnlineMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now()

            # Update last seen
            request.user.last_seen = now

            # Mark online
            request.user.is_online = True
            request.user.save(update_fields=["is_online", "last_seen"])

        response = self.get_response(request)
        return response

class DisableClientSideCachingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response