from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from .models import Petition, PetitionVote
from .forms import PetitionForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

#petition
@login_required
def petition_listings(request):
    petitions = Petition.objects.all().order_by('-date')
    return render(request, 'movies/petition_listings.html', {'petitions': petitions})

@login_required
def petition_create(request):
    if request.method == 'POST':
        form = PetitionForm(request.POST)
        if form.is_valid():
            petition = form.save(commit=False)
            petition.creator = request.user
            petition.save()
            return redirect('movies.petition_listings')
    else:
        form = PetitionForm()
    return render(request, 'movies/petition_create.html', {'form': form})

def petition_details(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)
    votes_count = petition.votes.count()
    user_voted = False
    if request.user.is_authenticated:
        user_voted = PetitionVote.objects.filter(petition=petition, user=request.user).exists()
    return render(request, 'movies/petition_details.html', {
        'petition': petition,
        'votes_count': votes_count,
        'user_voted': user_voted
    })

@login_required
def petition_vote(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)
    if PetitionVote.objects.filter(petition=petition, user=request.user).exists():
        return HttpResponseForbidden('You have already voted for this petition.')
    PetitionVote.objects.create(petition=petition, user=request.user)
    return redirect('movies.petition_details', petition_id=petition.id)
  