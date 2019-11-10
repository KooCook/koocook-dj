from .base import BaseController, ControllerResponseUnauthorised, JsonRequestHandler
from ..models import KoocookUser


def to_koocook_user(func):
    from django.db.models import Model

    def wrapper(controller: BaseController, *args, **kwargs):
        try:
            controller.request_fields['user'] = KoocookUser(user=controller.request_fields['user'])
        except Model.DoesNotExist:
            return ControllerResponseUnauthorised()

        if (len(args) > 0 and args[0] is not None) or len(kwargs) > 0:
            return func(controller, *args, **kwargs)
        else:
            return func(controller)
    return wrapper


class UserController(BaseController):
    def __init__(self, request_fields: dict):
        super().__init__(KoocookUser, request_fields)

    @property
    def user(self):
        return self.request_fields['user']

    @to_koocook_user
    def follow(self):
        user = KoocookUser.objects.get(user_id=self.request_fields['follower_id'])
        self.user.follow(user)
        return self.create()

    @to_koocook_user
    def unfollow(self):
        user = KoocookUser.objects.get(user_id=self.request_fields['follower_id'])
        self.user.unfollow(user)
        return self.create()


class UserHandler(JsonRequestHandler):
    pass
