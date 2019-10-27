from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'index.html')


def search_view(request):
    return render(request, 'search.html')

def detail_view(request):
    return render(request, 'detail.html')