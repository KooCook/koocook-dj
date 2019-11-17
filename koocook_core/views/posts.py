from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from .forms import PostForm
from ..models import Post


class UserPostStreamView(FormMixin, ListView):
    form_class = PostForm
    model = Post
    template_name = 'posts/index.html'
    ordering = ['-date_published']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_posts'] = self.object_list.filter(author__user__user=self.request.user)
        return context


class GuestPostStreamView(ListView):
    # template_name = 'posts/index.html'
    model = Post
    pass
