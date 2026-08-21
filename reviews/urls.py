from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    # Root URL is the login page (built-in view + our template)
    path('', LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True),
        name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/', views.home, name='home'),
]
