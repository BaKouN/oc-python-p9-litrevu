from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import SignupForm, TicketForm


def signup(request):
    """Register a new user, then log them in and send them to the feed."""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def home(request):
    """Landing page after login. Will become the combined feed later."""
    return render(request, 'reviews/home.html')


@login_required
def create_ticket(request):
    """Create a ticket owned by the current user."""
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('home')
    else:
        form = TicketForm()
    return render(request, 'reviews/create_ticket.html', {'form': form})
