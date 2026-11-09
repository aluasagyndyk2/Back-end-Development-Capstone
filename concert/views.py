import os
import requests
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending


def signup(request):
    form = SignUpForm(request.POST or None)
    message = ''
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            message = 'Username already exists.'
        else:
            user = User.objects.create_user(username=username, password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
    return render(request, 'signup.html', {'form': form, 'message': message})


def index(request):
    return render(request, 'index.html')


def service_data(variable, sample):
    url = os.environ.get(variable)
    if not url:
        return sample
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
    except (requests.RequestException, ValueError):
        return []


def songs(request):
    sample = [{'id': 1, 'title': 'duis faucibus accumsan odio curabitur convallis',
               'lyrics': 'Morbi non lectus. Aliquam sit amet diam in magna bibendum imperdiet. Nullam orci pede, venenatis non, sodales sed, tincidunt eu, felis.'}]
    return render(request, 'songs.html', {'songs': service_data('SONGS_URL', sample)})


def photos(request):
    sample = [{'id': 1, 'pic_url': 'https://dummyimage.com/136x100.png/5fa2dd/ffffff',
               'event_country': 'United States', 'event_state': 'District of Columbia',
               'event_city': 'Washington', 'event_date': '11/16/2022'}]
    return render(request, 'photos.html', {'photos': service_data('PICTURES_URL', sample)})


def login_view(request):
    form = LoginForm(request=request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def concerts(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    reservations = {row.concert_id: row.attending for row in ConcertAttending.objects.filter(user=request.user)}
    rows = [{'concert': concert, 'status': reservations.get(concert.id, '-')} for concert in Concert.objects.all()]
    return render(request, 'concerts.html', {'concerts': rows})


def concert_detail(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    concert = get_object_or_404(Concert, pk=id)
    reservation = ConcertAttending.objects.filter(concert=concert, user=request.user).first()
    return render(request, 'concert_detail.html', {'concert_details': concert,
        'status': reservation.attending if reservation else '-',
        'attending_choices': ConcertAttending.AttendingChoices.choices})


def concert_attendee(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if request.method == 'POST':
        try:
            concert_id = int(request.POST.get('concert_id', ''))
        except (TypeError, ValueError):
            return HttpResponseBadRequest('Invalid concert ID')
        concert = get_object_or_404(Concert, pk=concert_id)
        choice = request.POST.get('attendee_choice')
        if choice not in ConcertAttending.AttendingChoices.values:
            return HttpResponseBadRequest('Invalid attendance status')
        ConcertAttending.objects.update_or_create(concert=concert, user=request.user, defaults={'attending': choice})
    return HttpResponseRedirect(reverse('concerts'))
