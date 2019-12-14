from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.shortcuts import reverse

from .mixins import SignInRequiredMixin, PreferencesMixin
from .forms import BasicProfileForm, ExtendedProfileForm
from ..models import KoocookUser


class UserProfileInfoView(SignInRequiredMixin, UpdateView):
    model = User
    form_class = BasicProfileForm
    template_name = 'users/info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'info'
        return context


class UserSettingsInfoView(PreferencesMixin, UpdateView):
    model = KoocookUser
    form_class = ExtendedProfileForm
    template_name = 'users/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = 'pref'
        return context
