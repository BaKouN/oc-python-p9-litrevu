from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Review, Ticket, User, UserFollows

INPUT_CLASSES = 'input w-full'
TEXTAREA_CLASSES = 'textarea w-full'


class SignupForm(UserCreationForm):
    """Registration form bound to our custom User model."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASSES}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('password1', 'password2'):
            self.fields[name].widget.attrs['class'] = INPUT_CLASSES


class LoginForm(AuthenticationForm):
    """Login form with styled widgets."""

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': "Identifiants invalides. Veuillez réessayer.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = INPUT_CLASSES


class TicketForm(forms.ModelForm):
    """Create/edit a ticket."""

    class Meta:
        model = Ticket
        fields = ('title', 'description', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 5}),
            'image': forms.ClearableFileInput(attrs={'class': 'file-input w-full'}),
        }


class ReviewForm(forms.ModelForm):
    """Create/edit a review."""

    class Meta:
        model = Review
        fields = ('headline', 'rating', 'body')
        labels = {
            'headline': 'Titre',
            'rating': 'Note',
            'body': 'Commentaire',
        }
        widgets = {
            'headline': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'body': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 6}),
            'rating': forms.RadioSelect(
                choices=[(i, str(i)) for i in range(6)],
                attrs={'class': 'radio radio-primary'},
            ),
        }


class FollowForm(forms.Form):
    """Follow another user by username."""

    username = forms.CharField(
        max_length=150,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES}),
    )

    def __init__(self, *args, user=None, **kwargs):
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
        self.cleaned_data['target'] = target
        return username
