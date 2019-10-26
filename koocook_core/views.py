from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'index.html')


def search_view(request):
    keyword = request.GET.get("kw")
    return render(request, 'search.html')
