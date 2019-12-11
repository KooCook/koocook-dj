from django.http import HttpRequest
from django.conf import settings


def globalvars_processor(request: HttpRequest):
    return {'APP_VERSION': getattr(settings, 'APP_VERSION', '0.0.0.0')}
