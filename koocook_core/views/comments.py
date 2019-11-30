from django.http import HttpRequest, JsonResponse
from django.urls import resolve
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from ..models import Comment, Post, Recipe

# Deprecated
@login_required
@require_http_methods('POST')
def post_comment(request: HttpRequest):
    from ..models import Author
    author = Author.from_dj_user(request.user)
    item_id = request.POST.get('item_id')
    comment_fields = {field: val for (field, val) in request.POST.dict().items()
                      if field in Comment.field_names()}
    comment_fields.update({'author': author})

    current_url = resolve(request.path_info).route
    if 'recipe' in current_url:
        comment_fields.update({'reviewed_recipe': Recipe.objects.get(pk=item_id)})
    elif 'post' in current_url:
        comment_fields.update({'reviewed_post': Post.objects.get(pk=item_id)})
    elif 'comment' in current_url:
        comment_fields.update({'reviewed_comment': Comment.objects.get(pk=item_id)})
    comment = Comment(**comment_fields)
    comment.save()
    return JsonResponse({'current': comment.as_json})
