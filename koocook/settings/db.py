from decouple import config as _config
from .dirs import BASE_DIR as _BASE_DIR

DATABASE_NAME = _config('DATABASE_NAME', (_BASE_DIR / 'db.sqlite3').as_posix())

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': _config('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': DATABASE_NAME,
        'USER': _config('DATABASE_USERNAME', 'username'),
        'PASSWORD': _config('DATABASE_PASSWORD', 'password'),
        'HOST': _config('DATABASE_HOST', '127.0.0.1'),
        'PORT': _config('DATABASE_PORT', '5432'),
        'TEST': {
            'NAME': _config('TEST_DATABASE_NAME', 'test_' + DATABASE_NAME),
        }
    }
}
