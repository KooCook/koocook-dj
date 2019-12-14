from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .forms import FeedbackForm
from ..models import Author


@login_required
def post_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = Author.objects.get(pk=request.user.id)
            post.save()
            return redirect('../')
    else:
        form = FeedbackForm()
    return render(request, 'feedback/index.html', {'form': form})
