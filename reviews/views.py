from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReviewForm, SignupForm, TicketForm
from .models import Review, Ticket


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
    reviews = Review.objects.filter(user=request.user).order_by('-time_created')
    # Ticket ids the current user already reviewed: used to hide the link.
    reviewed_ids = set(reviews.values_list('ticket_id', flat=True))
    return render(request, 'reviews/home.html', {
        'tickets': tickets,
        'reviews': reviews,
        'reviewed_ids': reviewed_ids,
    })


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
    

@login_required
def create_review(request, ticket_id):
    """Post a review in response to an existing ticket."""
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    # One review per user per ticket. The hidden link is UX; this is the guard.
    if Review.objects.filter(ticket=ticket, user=request.user).exists():
        raise PermissionDenied
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('home')
    else:
        form = ReviewForm()
    return render(request, 'reviews/create_review.html', {'form': form, 'ticket': ticket})


@login_required
def edit_review(request, review_id):
    """Edit a review. Author only."""
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'reviews/edit_review.html', {'form': form, 'review': review})


@login_required
def delete_review(request, review_id):
    """Delete a review. Author only, POST only."""
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        review.delete()
        return redirect('home')
    return render(request, 'reviews/delete_review.html', {'review': review})


@login_required
def create_ticket_and_review(request):
    """Create a ticket and its review in one step (two forms, one POST)."""
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        # all([...]) validates BOTH forms; `and` would stop at the first failure
        # and hide the second form's errors from the user.
        if all([ticket_form.is_valid(), review_form.is_valid()]):
            with transaction.atomic():
                ticket = ticket_form.save(commit=False)
                ticket.user = request.user
                ticket.save()
                review = review_form.save(commit=False)
                review.user = request.user
                review.ticket = ticket
                review.save()
            return redirect('home')
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()
    return render(request, 'reviews/create_ticket_and_review.html', {
        'ticket_form': ticket_form,
        'review_form': review_form,
    })
