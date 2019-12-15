import logging
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.shortcuts import reverse

from .mixins import SignInRequiredMixin, PreferencesMixin
from .forms import BasicProfileForm, ExtendedProfileForm
from ..models import KoocookUser

LOGGER = logging.getLogger(__name__)


class UserProfileInfoView(SignInRequiredMixin, UpdateView):
    model = User
    form_class = BasicProfileForm
    template_name = 'users/info.html'

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            LOGGER.info(f"{request.user.username} has changed their profile")
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'info'
        return context


class UserSettingsInfoView(PreferencesMixin, UpdateView):
    model = KoocookUser
    form_class = ExtendedProfileForm
    template_name = 'users/settings.html'

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            LOGGER.info(f"{request.user.username} has changed their preferences")
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'pref'
        return context
