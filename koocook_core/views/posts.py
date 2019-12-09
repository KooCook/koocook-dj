from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from .forms import PostForm
from ..models import Author, Post


class UserPostStreamView(FormMixin, ListView):
    form_class = PostForm
    model = Post
    template_name = 'posts/index.html'
    ordering = ['-date_published']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['current_author'] = Author.objects.get(user__user=self.request.user)
            context['user_posts'] = self.object_list.filter(author__user__user=self.request.user)
        context['posts'] = self.object_list.all()
        return context


class GuestPostStreamView(ListView):
    template_name = 'posts/index.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object_list.all()
        return context
