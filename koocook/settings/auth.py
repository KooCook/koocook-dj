from decouple import config as _config

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


LOGIN_REDIRECT_URL = _config('LOGIN_REDIRECT_URL', '/')
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = _config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', cast=str)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = _config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', cast=str)
SOCIAL_AUTH_PIPELINE = (

    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'koocook_auth.pipelines.associate_social_profile'
)
