from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .forms import FeedbackForm
from ..models import Feedback


# class UserFeedback(FormMixin, ListView):
#     form_class = FeedbackForm
#     model = Feedback
#     template_name = 'feedback/index.html'
#     ordering = ['-date_published']
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user_posts'] = self.object_list.filter(author__user__user=self.request.user)
#         return context


@login_required
def post_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        form.save()

        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('index')
    else:
        form = FeedbackForm()
    return render(request, 'feedback/index.html', {'form': form})
