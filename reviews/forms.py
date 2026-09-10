from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Review, Ticket, User


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


class ReviewForm(forms.ModelForm):
    """Create/edit a review. Rating rendered as 0–5 radio buttons."""

    class Meta:
        model = Review
        fields = ('headline', 'rating', 'body')
        labels = {
            'headline': 'Titre',
            'rating': 'Note',
            'body': 'Commentaire',
        }
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, str(i)) for i in range(6)]),
        }