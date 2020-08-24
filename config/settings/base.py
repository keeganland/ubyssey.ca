"""
base.py, default settings, originating from Dispatch module.
Use: place .env file containing app configuration in /ubyssey.ca/

Part of the 12factor app philosophy is to keep config seperate from code. Typically, the environment variables are used for the config.
This code's primary job therefore ought to be retrieving the config from the environment rather than hardcoding in config settings.

Having these imported from Dispatch is too "magical" to be desirable, even if Dispatch is an explict dependency.
Don't Repeat Yourself, yes, but "redundancy" isn't bad if it's accross what are nominally entirely different projects!
More Pythonic is: Explicit rather than implicit.

Environment variable stuff is based on the following document from Google CodeLabs
https://codelabs.developers.google.com/codelabs/cloud-run-django/index.html?index=..%2F..index#5
"""

import os
import sys
import environ
from dispatch.apps import DispatchConfig

BASE_DIR = environ.Path(__file__) - 3
DISPATCH_APP_DIR = DispatchConfig.path

env = environ.Env() # will reinitialize later once "earliest" configs have been set
FORCE_GOOGLE_AUTHENTICATION = env.bool("FORCE_GOOGLE_AUTHENTICATION", default=False)

# If we don't have Google app credentials, grab them
if not "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(BASE_DIR, 'client-secret.json')

# Look for the environment variables file in the root directory
# Absolute rather than relative path here, to play nice with Google App Engine
env_file = os.path.join(BASE_DIR, 'tmp/.env')

# In production we can get .envfrom Google Cloud if we don't have it. This requires authentication.
# Set FORCE_GOOGLE_AUTHENTICATION
if FORCE_GOOGLE_AUTHENTICATION or (os.environ['DJANGO_SETTINGS_MODULE'] == 'config.settings.production' and not os.path.isfile(env_file)):
    import google.auth
    from google.cloud import secretmanager as sm
    env_file = os.path.join('/tmp/.env')

    try:
        _, project = google.auth.default()

        if project:
            client = sm.SecretManagerServiceClient()
            path = client.secret_version_path(project, "ubyssey_env_configs", "latest")
            payload = client.access_secret_version(path).payload.data.decode("UTF-8")
            with open(env_file, "w") as f:
                f.write(payload)
        else:
            sys.stderr.write("\nError: Unsuccessful attempt to get a project from google.auth!\n")      
    except Exception as ex:       
        sys.stderr.write("\nError in trying to generate .env file using Google application credentials!\n")
        raise ex

# We now have an .env file.
# An env object from environ library simplifies reading/writing env vars.
# We intialize this object, setting castings and defaults (an advantage of the environ library over simply using the os library)
env = environ.Env(
    #set casting and defaults for config vars which are to be read from environment

    # Development defaults
    # VERSION=(str,'0.0.0'),
    DEBUG=(bool,False),
    ORGANIZATION_NAME = (str, 'Ubyssey'),
    
    # URL defaults
    STATIC_URL = (str,'/static/'),
    MEDIA_URL = (str,'/media/'),
    ADS_TXT_URL = (str, 'https://ubyssey.storage.googleapis.com/ads.txt'),
    ROOT_URLCONF = (str,'ubyssey.urls'),

    # Time zone defaults
    USE_TZ=(bool,True),
    TIME_ZONE=(str,'Canada/Pacific'),

    # Database defaults:
    SQL_HOST = (str, 'db'),
    SQL_DATABASE= (str, 'ubyssey'),
    SQL_USER = (str, 'root'),
    SQL_PASSWORD = (str, 'ubyssey'),

    # Keys
    SECRET_KEY = (str, 'thisisakey'),
    NOTIFICATION_KEY= (str, 'thisisakeytoo'),

    # delete me
    SECRET_URL = (str, 'somethingsilly')
)

# Read the .env file into os.environ.
environ.Env.read_env(env_file)

# Set Django's configs to the values taken from the .env file (or else to their defaults listed above)
ORGANIZATION_NAME = env('ORGANIZATION_NAME') # Used for registration/invitation
DEBUG = env('DEBUG')

USE_TZ = env('USE_TZ')
TIME_ZONE = env('TIME_ZONE')

STATIC_URL = env('STATIC_URL')
MEDIA_URL = env('MEDIA_URL')
ADS_TXT_URL = env('ADS_TXT_URL')
ROOT_URLCONF = env('ROOT_URLCONF')

# Initialize the databases.
# Note it should be possible to parse all this information in a single line:
# DATABASES = {'default': env.db('DATABASE_URL')}
# However, Google Cloud Services does not seem to like providing an easily parsable URL for such purposes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': env('SQL_HOST'),
        'NAME': env('SQL_DATABASE'),
        'USER': env('SQL_USER'),
        'PASSWORD': env('SQL_PASSWORD'),
        'PORT': '3306',
    },
}

# Set secret keys
SECRET_KEY = env('SECRET_KEY')
NOTIFICATION_KEY = env('NOTIFICATION_KEY')

# Application definition
INSTALLED_APPS = [
    # 'whitenoise.runserver_nostatic', # uncomment for testing "production-like" serving of collected static files with DEBUG=False
    'ubyssey', #For some reason using ubyssey.apps.UbysseyConfig breaks static file finding?
    'dispatch.apps.DispatchConfig',
    'newsletter.apps.NewsletterConfig',
    'dispatchwagtail.apps.DispatchwagtailConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'rest_framework.authtoken',

    # wagtail stuff
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',

    'modelcluster',
    'taggit',
]

# Replace default user model
AUTH_USER_MODEL = 'dispatch.User'

API_URL = '/api/'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Templates
TEMPLATES = [
    {
        'NAME': 'app_dirs',
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
    {
        'NAME': 'dispatch',
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
			DISPATCH_APP_DIR('templates')
        ],
    },
]

# REST framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'UNICODE_JSON': True,
    'PAGE_SIZE': 10,
    'DATETIME_INPUT_FORMATS': ['iso-8601']
}

STATICFILES_DIRS = []

MIDDLEWARE = [												 											 												   
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',													
]

GS_LOCATION = None
GS_STORAGE_BUCKET_NAME = None
GS_USE_SIGNED_URLS = False

PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'CA'

PASSWORD_RESET_TIMEOUT_DAYS = 1

SECRET_URL = env('SECRET_URL')
WAGTAIL_SITE_NAME = 'The Ubyssey'
WAGTAIL_USER_EDIT_FORM = 'dispatchwagtail.forms.DispatchUserEditForm'
WAGTAIL_USER_CREATION_FORM = 'dispatchwagtail.forms.DispatchUserCreationForm'
WAGTAIL_USER_CUSTOM_FIELDS = ['person', 'is_active']
