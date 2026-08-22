from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Ticket, User


class SignupForm(UserCreationForm):
    """Registration form bound to our custom User model."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)


class TicketForm(forms.ModelForm):
    """Create/edit a ticket. Fields generated from the Ticket model."""

    class Meta:
        model = Ticket
        fields = ('title', 'description', 'image')
