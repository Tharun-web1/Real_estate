from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    """
    Custom authentication backend.

    Allows users to log in using their username, email address, or phone number.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to fetch the user by searching the username, email, and phone fields.
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username) | Q(phone__iexact=username)
            )
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between a user not existing and a user existing with a
            # wrong password.
            UserModel().set_password(password)
            return
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user