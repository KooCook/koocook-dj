from decouple import config
from .dirs import BASE_DIR

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': config('DATABASE_NAME', (BASE_DIR / 'db.sqlite3').as_posix()),
        'USER': config('DATABASE_USERNAME', 'username'),
        'PASSWORD': config('DATABASE_PASSWORD', 'password'),
        'HOST': config('DATABASE_HOST', '127.0.0.1'),
        'PORT': config('DATABASE_PORT', '5432')
    }
}
