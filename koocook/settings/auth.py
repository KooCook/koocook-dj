import os

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/core/'

SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "513269157789-5pi2ubk2jeffu1e4emb1cjhe468cmigk.apps.googleusercontent.com" # os.environ('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "yt2zMD8b-VTLQW8dkxVsgXm7" # os.environ('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')
