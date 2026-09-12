from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Review, Ticket, User, UserFollows


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

class FollowForm(forms.Form):
    """Follow another user by username. All the rules live in clean_username."""

    username = forms.CharField(max_length=150, label="Nom d'utilisateur")

    def __init__(self, *args, user=None, **kwargs):
        # The current user is needed to reject self-follow and duplicates.
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            target = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Cet utilisateur n'existe pas.")
        if target == self.user:
            raise forms.ValidationError('Vous ne pouvez pas vous suivre vous-même.')
        if UserFollows.objects.filter(user=self.user, followed_user=target).exists():
            raise forms.ValidationError('Vous suivez déjà cet utilisateur.')
        # Hand the resolved User to the view so it does not query again.
        self.cleaned_data['target'] = target
        return username
