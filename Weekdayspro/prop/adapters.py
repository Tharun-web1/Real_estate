from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.contrib import messages

User = get_user_model()

class NoAutoSignupSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        if request.user.is_authenticated:
            return

        email = sociallogin.account.extra_data.get('email')

        if not email:
            messages.error(request, "Unable to retrieve email from Google account.")
            raise ImmediateHttpResponse(redirect('/login/'))

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            messages.error(
                request,
                "We couldn’t find an account with this email. Please register first."
            )
            # Redirect to the **correct registration page**
            raise ImmediateHttpResponse(redirect('/login/register'))

        # Connect the social account to the existing user
        sociallogin.connect(request, user)
