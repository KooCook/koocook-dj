from .base import ControllerResponseUnauthorised, ControllerResponseForbidden
from ..models import KoocookUser, Author


def apply_author_from_session(func):
    def wrapper(controller, *args, **kwargs):
        try:
            controller.request_fields['author'] = Author.from_dj_user(controller.request.user)
        except Author.DoesNotExist:
            return ControllerResponseUnauthorised()

        if (len(args) > 0 and args[0] is not None) or len(kwargs) > 0:
            return func(controller, **kwargs)
        else:
            return func(controller)
    return wrapper


def to_koocook_user(func):
    def wrapper(controller, *args, **kwargs):
        if not controller.user.is_authenticated:
            return ControllerResponseUnauthorised()
        try:
            controller.request_fields['user'] = KoocookUser.objects.get(user=controller.request_fields['user'])
        except KoocookUser.DoesNotExist:
            return ControllerResponseUnauthorised()

        if (len(args) > 0 and args[0] is not None) or len(kwargs) > 0:
            return func(controller, *args, **kwargs)
        else:
            return func(controller)
    return wrapper



