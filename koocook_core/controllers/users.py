from django.db.models import Model
from django.contrib.auth.models import AnonymousUser

from .base import BaseController, ControllerResponseUnauthorised, JsonRequestHandler, ControllerResponse
from ..models import KoocookUser
from ..views import UserProfileInfoView, UserSettingsInfoView
from .decorators import to_koocook_user


class UserController(BaseController):
    def __init__(self, request_fields: dict):
        super().__init__(KoocookUser, request_fields)

    @classmethod
    def default(cls):
        return cls({})

    @property
    def user(self) -> KoocookUser:
        return self.request_fields['user']

    @property
    def preferences(self):
        return self._preferences

    @to_koocook_user
    def view_profile(self):
        return UserProfileInfoView.as_view()(self.request, pk=self.user.pk)

    @to_koocook_user
    def view_settings_info(self):
        return UserSettingsInfoView.as_view()(self.request, pk=self.user.pk)

    @to_koocook_user
    def set_preferences(self):
        self.user.formal_preferences['allow_glut'] = 'False'
        self.user.save()
        return ControllerResponse(status_text='Preferences set', obj=self.user.preferences)

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
            'GET': 'view_profile',
            'POST': 'view_profile',
            'pref': {
                'GET': 'view_settings_info',
                'POST': 'view_settings_info',
            },
            'pref:set': {
                'POST': 'set_preferences',
            },
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


