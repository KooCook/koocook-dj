from django.contrib.auth import logout
from django.shortcuts import redirect, render


# Create your views here.
def index(request):
    return render(request, 'index.html')


def logout_view(request):
    logout(request)
    return redirect("koocook_core:index")
