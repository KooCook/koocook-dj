import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
