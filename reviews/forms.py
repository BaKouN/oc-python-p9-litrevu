from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    """Registration form bound to our custom User model."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)
