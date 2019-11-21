from django.http import HttpRequest, JsonResponse
from django.db.models import Model
from django.shortcuts import redirect

from ..models import Author, Comment


def restful_if_ajax(request, data, status=200, to_section: str = None):
    request.path = f'{request.path}#{to_section}' if to_section else request.path
    if request.is_ajax():
        return JsonResponse(data, status=status)
    else:
        return redirect(request.path)


def allow_post_comments(model: Model, id_name: str):
    def decorator(function):
        def wrapper(request: HttpRequest, **kwargs):

            thread_id = kwargs[id_name]
            print(thread_id)
            if request.user.is_authenticated:
                if request.method == 'POST':
                    comment_fields = {field: val for (field, val) in request.POST.dict().items()
                                      if field in Comment.field_names()}
                    thread = model.objects.get(pk=thread_id)
                    if thread:
                        comment_fields['reviewed_recipe'] = thread
                        try:
                            found_author = Author.objects.get(user__user=request.user)
                            comment_fields['author'] = found_author
                            found, created = Comment.objects.get_or_create(**comment_fields)
                            if created:
                                return restful_if_ajax(request, {'status': 'Posted'}, to_section='comments')
                            else:
                                found.body = comment_fields['body']
                                if found.body:
                                    found.save()
                                    return restful_if_ajax(request, {'status': 'Edits published'},
                                                           to_section='comments')
                                else:
                                    return restful_if_ajax(request, {'status': 'Bad request'}, 400)
                        except Author.DoesNotExist:
                            return JsonResponse({'status': 'Forbidden'}, status=403)
                    else:
                        return JsonResponse({'status': 'thread not found'}, status=404)
                else:
                    return function(request, thread_id)
            else:
                return JsonResponse({'status': 'Unauthorised'}, status=401)
        return wrapper
    return decorator

