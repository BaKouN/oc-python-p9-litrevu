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
    path('signup/', views.signup, name='signup'),
    path('feed/', views.feed, name='feed'),
    path('posts/', views.posts, name='posts'),
    path('ticket/create/', views.create_ticket, name='create_ticket'),
    path('ticket/<int:ticket_id>/edit/', views.edit_ticket, name='edit_ticket'),
    path('ticket/<int:ticket_id>/delete/', views.delete_ticket, name='delete_ticket'),
    path('ticket/<int:ticket_id>/review/', views.create_review, name='create_review'),
    path('review/create/', views.create_ticket_and_review, name='create_ticket_and_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('follows/', views.follows, name='follows'),
    path('follows/<int:user_id>/unfollow/', views.unfollow, name='unfollow'),
]
