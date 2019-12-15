from .dirs import LOGS_DIR
from decouple import config as _config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR/'django.log',
            'maxBytes': 1024*1024*3,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'app_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'app.log',
            'maxBytes': 1024 * 1024 * 3,
            'backupCount': 2,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': _config('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'koocook_core': {
            'handlers': ['app_file', 'console'],
            'level': _config('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'koocook_auth': {
            'handlers': ['app_file', 'console'],
            'level': _config('DJANGO_LOG_LEVEL', 'INFO'),
        }
    },
}