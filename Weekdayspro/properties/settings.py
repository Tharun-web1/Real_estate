from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-2f_slbu-aqv__=!8v=9#-+m=(ar_sxl3#mk43_r%l&yjz0kag_'
DEBUG = True


AUTH_USER_MODEL = 'prop.User'

# -------------------------
# Allowed Hosts and CSRF
# -------------------------
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "weekdaysproperties.com",
    "www.weekdaysproperties.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://weekdaysproperties.com",
    "https://www.weekdaysproperties.com",
]


RAZORPAY_KEY_ID = "rzp_test_SIM6aTOpqUfpzz"
RAZORPAY_KEY_SECRET = "u2z1gC1RqGiXIQSYvdvabAai"

# -------------------------
# Site ID (required by allauth)
# -------------------------
SITE_ID = 1

# -------------------------
# Authentication Backends
# -------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # default backend
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth backend
)

LOGIN_REDIRECT_URL = '/'      # redirect after login
LOGOUT_REDIRECT_URL = '/'     # redirect after logout

# -------------------------
# Allauth Social Adapter
# -------------------------
# Replace 'yourapp' with your actual Django app name, e.g., 'prop.adapters'
SOCIALACCOUNT_ADAPTER = 'prop.adapters.NoAutoSignupSocialAccountAdapter'

# -------------------------
# Django-allauth Settings
# -------------------------
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'  # change to 'mandatory' in production

# -------------------------
# Social Account Providers
# -------------------------
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '648445278436-94ei3b9sgivtkhp114qn1dtkp9s8hr6b.apps.googleusercontent.com',
            'secret': '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',  # replace with your actual secret
            'key': ''
        }
    },
    'facebook': {
        'APP': {
            'client_id': 'YOUR_FACEBOOK_APP_ID',  # replace with your FB app ID
            'secret': 'YOUR_FACEBOOK_APP_SECRET',  # replace with your FB secret
            'key': ''
        }
    }
}

# -------------------------
# Installed Apps
# -------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    
    'prop',   # your app 
]


SOCIALACCOUNT_ADAPTER = 'prop.adapters.NoAutoSignupSocialAccountAdapter'
SOCIALACCOUNT_LOGIN_ON_GET = True
LOGIN_URL = '/login/'
SOCIALACCOUNT_AUTO_SIGNUP = False


# -------------------------
# Middleware
# -------------------------
# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # required
    'prop.middleware.DisableClientSideCachingMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Allauth Settings
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
SOCIALACCOUNT_ADAPTER = 'prop.adapters.NoAutoSignupSocialAccountAdapter'

# -------------------------
# Templates (must include request context processor)
# -------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # your templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # REQUIRED for allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'properties.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'), # Global templates
            os.path.join(BASE_DIR, 'lucky', 'templates'), # Templates for the 'lucky' app
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'prop.context_processors.notification_counts',
            ],
        },
    },
]

WSGI_APPLICATION = 'properties.wsgi.application'

# ------------------------------
# DATABASE
# ------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [  
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
# ✅ Add the path to your top-level static directory
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'lucky/static'), # Static files for the 'lucky' app
]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ Custom user model
AUTH_USER_MODEL = 'prop.User'

# ✅ Custom Authentication Backend for multi-field login
AUTHENTICATION_BACKENDS = [
    'prop.backends.EmailOrPhoneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ✅ Media setup
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL="/login/"

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ASGI_APPLICATION = "properties.asgi.application"
MIDDLEWARE += ["prop.middleware.OnlineMiddleware"]
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}