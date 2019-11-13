from django.db.models import Model
from django.contrib.auth.models import AnonymousUser

from .base import BaseController, ControllerResponseUnauthorised, JsonRequestHandler, ControllerResponse
from ..models import KoocookUser


def to_koocook_user(func):
    def wrapper(controller: BaseController, *args, **kwargs):
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


class UserController(BaseController):
    def __init__(self, request_fields: dict):
        super().__init__(KoocookUser, request_fields)

    @classmethod
    def default(cls):
        return cls({})

    @property
    def user(self) -> KoocookUser:
        return self.request_fields['user']

    @to_koocook_user
    def get_following(self):
        return ControllerResponse(status_text='Retrieved', obj=list(self.user.following.all()))

    @to_koocook_user
    def follow(self):
        followee = KoocookUser.objects.get(user_id=self.request_fields['followee_id'])
        self.user.follow(followee)
        return ControllerResponse(status_text='Followed', obj=followee)

    @to_koocook_user
    def unfollow(self):
        followee = KoocookUser.objects.get(user_id=self.request_fields['followee_id'])
        self.user.unfollow(followee)
        return ControllerResponse(status_text='Unfollowed')


class UserHandler(JsonRequestHandler):
    def __init__(self):
        super().__init__(UserController.default())
        self.handler_map = {
            'follow': {
                'GET': 'get_following',
                'POST': 'follow'
            },
            'unfollow': {
                'POST': 'unfollow'
            }
        }

    @classmethod
    def instance(cls):
        return cls()


