from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from itertools import chain

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import CharField, Q, Value
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import FollowForm, ReviewForm, SignupForm, TicketForm
from .models import Review, Ticket, UserFollows


def signup(request):
    """Register a new user, then log them in and send them to the feed."""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def feed(request):
    """Combined feed: tickets and reviews from three sources, newest first."""
    followed_ids = UserFollows.objects.filter(
        user=request.user).values_list('followed_user', flat=True)
    tickets = Ticket.objects.filter(
        Q(user=request.user) | Q(user__in=followed_ids)
    ).annotate(content_type=Value('TICKET', CharField()))
    reviews = Review.objects.filter(
        Q(user=request.user) | Q(user__in=followed_ids) | Q(ticket__user=request.user)
    ).annotate(content_type=Value('REVIEW', CharField()))
    posts = sorted(chain(tickets, reviews), key=lambda p: p.time_created, reverse=True)
    reviewed_ids = set(
        Review.objects.filter(user=request.user).values_list('ticket_id', flat=True))
    return render(request, 'reviews/feed.html', {
        'posts': posts,
        'reviewed_ids': reviewed_ids,
    })


@login_required
def posts(request):
    """The current user's own tickets and reviews, with edit/delete actions."""
    tickets = Ticket.objects.filter(user=request.user).annotate(
        content_type=Value('TICKET', CharField()))
    reviews = Review.objects.filter(user=request.user).annotate(
        content_type=Value('REVIEW', CharField()))
    posts = sorted(chain(tickets, reviews), key=lambda p: p.time_created, reverse=True)
    return render(request, 'reviews/posts.html', {'posts': posts})


@login_required
def create_ticket(request):
    """Create a ticket owned by the current user."""
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('feed')
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
            return redirect('posts')
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
        return redirect('posts')
    return render(request, 'reviews/delete_ticket.html', {'ticket': ticket})


@login_required
def create_review(request, ticket_id):
    """Post a review in response to an existing ticket."""
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if Review.objects.filter(ticket=ticket, user=request.user).exists():
        raise PermissionDenied
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('feed')
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
            return redirect('posts')
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
        return redirect('posts')
    return render(request, 'reviews/delete_review.html', {'review': review})


@login_required
def create_ticket_and_review(request):
    """Create a ticket and its review in one step (two forms, one POST)."""
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if all([ticket_form.is_valid(), review_form.is_valid()]):
            with transaction.atomic():
                ticket = ticket_form.save(commit=False)
                ticket.user = request.user
                ticket.save()
                review = review_form.save(commit=False)
                review.user = request.user
                review.ticket = ticket
                review.save()
            return redirect('feed')
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()
    return render(request, 'reviews/create_ticket_and_review.html', {
        'ticket_form': ticket_form,
        'review_form': review_form,
    })


@login_required
def follows(request):
    """Follow a user by name; list who I follow and who follows me."""
    if request.method == 'POST':
        form = FollowForm(request.POST, user=request.user)
        if form.is_valid():
            target = form.cleaned_data['target']
            UserFollows.objects.create(user=request.user, followed_user=target)
            messages.success(request, f'Vous suivez maintenant {target.username}.')
            return redirect('follows')
    else:
        form = FollowForm(user=request.user)
    following = request.user.following.select_related('followed_user')
    followers = request.user.followed_by.select_related('user')
    return render(request, 'reviews/follows.html', {
        'form': form,
        'following': following,
        'followers': followers,
    })


@login_required
@require_POST
def unfollow(request, user_id):
    """Stop following a user. POST only."""
    follow = get_object_or_404(UserFollows, user=request.user, followed_user_id=user_id)
    follow.delete()
    messages.success(request, f'Vous ne suivez plus {follow.followed_user.username}.')
    return redirect('follows')
