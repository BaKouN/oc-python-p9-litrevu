from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    """Landing page after login. Will become the combined feed later."""
    return render(request, 'reviews/home.html')
