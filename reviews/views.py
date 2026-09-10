from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SignupForm, TicketForm
from .models import Ticket


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
    tickets = Ticket.objects.filter(user=request.user).order_by('-time_created')
    return render(request, 'reviews/home.html', {'tickets': tickets})


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


@login_required
def edit_ticket(request, ticket_id):
    """Edit a ticket. Author only."""
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if ticket.user != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'reviews/edit_ticket.html', {'form': form, 'ticket': ticket})


@login_required
def delete_ticket(request, ticket_id):
    """Delete a ticket. Author only, POST only."""
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if ticket.user != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        ticket.delete()
        return redirect('home')
    return render(request, 'reviews/delete_ticket.html', {'ticket': ticket})
