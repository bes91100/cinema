import io

import pyotp
import pytest
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from PIL import Image
from rest_framework.test import APIClient

from cinema.models import Genre, Hall, Movie, MoviePhoto, Session, Ticket


def make_image():
    file = io.BytesIO()
    Image.new('RGB', (10, 10)).save(file, 'PNG')
    return SimpleUploadedFile('test.png', file.getvalue(), content_type='image/png')


@pytest.fixture
def user():
    return User.objects.create_user(username='test', password='test')


@pytest.fixture
def api_client(user):
    cache.clear()
    client = APIClient()
    client.force_login(user)
    return client


@pytest.fixture
def otp(api_client, user):
    cache.set(f'otp_good_{user.id}', True)


@pytest.mark.django_db
class TestGenresViewSet:
    def test_list(self, api_client, user):
        genre = baker.make(Genre, user=user)

        r = api_client.get('/api/genres/')
        data = r.json()

        assert len(data) == 1
        assert data[0]['name'] == genre.name

    def test_create(self, api_client, user):
        r = api_client.post('/api/genres/', {'name': 'Комедия'})

        genre = Genre.objects.get(id=r.json()['id'])
        assert genre.name == 'Комедия'
        assert genre.user == user

    def test_delete(self, api_client, user, otp):
        genres = baker.make(Genre, user=user, _quantity=10)

        api_client.delete(f'/api/genres/{genres[0].id}/')

        data = api_client.get('/api/genres/').json()
        assert len(data) == 9
        assert genres[0].id not in [i['id'] for i in data]

    def test_update(self, api_client, user, otp):
        genre = baker.make(Genre, user=user)

        r = api_client.put(f'/api/genres/{genre.id}/', {'name': 'Драма'})

        genre.refresh_from_db()
        assert r.json()['name'] == genre.name == 'Драма'


@pytest.mark.django_db
class TestMoviesViewSet:
    def test_list(self, api_client, user):
        movie = baker.make(Movie, user=user)

        data = api_client.get('/api/movies/').json()

        assert len(data) == 1
        assert data[0]['title'] == movie.title

    def test_create(self, api_client, user, settings, tmp_path):
        settings.MEDIA_ROOT = tmp_path
        genre = baker.make(Genre, user=user)

        r = api_client.post('/api/movies/', {
            'title': 'Фильм',
            'year': 2020,
            'duration': 120,
            'genre': genre.id,
            'picture': make_image(),
        })

        movie = Movie.objects.get(id=r.json()['id'])
        assert movie.title == 'Фильм'
        assert movie.genre == genre
        assert movie.picture

    def test_delete(self, api_client, user, otp):
        movies = baker.make(Movie, user=user, _quantity=10)

        api_client.delete(f'/api/movies/{movies[0].id}/')

        data = api_client.get('/api/movies/').json()
        assert len(data) == 9
        assert movies[0].id not in [i['id'] for i in data]

    def test_update(self, api_client, user, otp):
        movie = baker.make(Movie, user=user)

        api_client.put(f'/api/movies/{movie.id}/', {'title': 'Новое', 'year': 1999, 'duration': 90})

        movie.refresh_from_db()
        assert movie.title == 'Новое'
        assert movie.year == 1999


@pytest.mark.django_db
class TestMoviePhotosViewSet:
    def test_list(self, api_client, user):
        baker.make(MoviePhoto, user=user, picture='test.png')

        data = api_client.get('/api/movie-photos/').json()

        assert len(data) == 1

    def test_create(self, api_client, user, settings, tmp_path):
        settings.MEDIA_ROOT = tmp_path
        movie = baker.make(Movie, user=user)

        r = api_client.post('/api/movie-photos/', {'movie': movie.id, 'picture': make_image()})

        photo = MoviePhoto.objects.get(id=r.json()['id'])
        assert photo.movie == movie

    def test_delete(self, api_client, user, otp):
        photos = baker.make(MoviePhoto, user=user, picture='test.png', _quantity=10)

        api_client.delete(f'/api/movie-photos/{photos[0].id}/')

        data = api_client.get('/api/movie-photos/').json()
        assert len(data) == 9

    def test_update(self, api_client, user, otp, settings, tmp_path):
        settings.MEDIA_ROOT = tmp_path
        photo = baker.make(MoviePhoto, user=user, picture='test.png')
        movie = baker.make(Movie, user=user)

        api_client.put(f'/api/movie-photos/{photo.id}/', {'movie': movie.id, 'picture': make_image()})

        photo.refresh_from_db()
        assert photo.movie == movie


@pytest.mark.django_db
class TestHallsViewSet:
    def test_list(self, api_client, user):
        hall = baker.make(Hall, user=user)

        data = api_client.get('/api/halls/').json()

        assert len(data) == 1
        assert data[0]['name'] == hall.name

    def test_create(self, api_client, user):
        r = api_client.post('/api/halls/', {'name': 'Зал 1', 'capacity': 100})

        hall = Hall.objects.get(id=r.json()['id'])
        assert hall.name == 'Зал 1'
        assert hall.capacity == 100

    def test_delete(self, api_client, user, otp):
        halls = baker.make(Hall, user=user, _quantity=10)

        api_client.delete(f'/api/halls/{halls[0].id}/')

        data = api_client.get('/api/halls/').json()
        assert len(data) == 9

    def test_update(self, api_client, user, otp):
        hall = baker.make(Hall, user=user)

        api_client.put(f'/api/halls/{hall.id}/', {'name': 'VIP', 'capacity': 20})

        hall.refresh_from_db()
        assert hall.name == 'VIP'


@pytest.mark.django_db
class TestSessionsViewSet:
    def test_list(self, api_client, user):
        session = baker.make(Session, user=user)

        data = api_client.get('/api/sessions/').json()

        assert len(data) == 1
        assert data[0]['price'] == session.price

    def test_create(self, api_client, user):
        movie = baker.make(Movie, user=user)
        hall = baker.make(Hall, user=user)

        r = api_client.post('/api/sessions/', {
            'movie': movie.id,
            'hall': hall.id,
            'start': '2026-10-20T18:00',
            'price': 400,
        })

        session = Session.objects.get(id=r.json()['id'])
        assert session.movie == movie
        assert session.price == 400

    def test_delete(self, api_client, user, otp):
        sessions = baker.make(Session, user=user, _quantity=10)

        api_client.delete(f'/api/sessions/{sessions[0].id}/')

        data = api_client.get('/api/sessions/').json()
        assert len(data) == 9

    def test_update(self, api_client, user, otp):
        session = baker.make(Session, user=user)

        api_client.put(f'/api/sessions/{session.id}/', {
            'movie': session.movie.id,
            'hall': session.hall.id,
            'start': '2026-11-01T20:30',
            'price': 650,
        })

        session.refresh_from_db()
        assert session.price == 650


@pytest.mark.django_db
class TestTicketsViewSet:
    def test_list(self, api_client, user):
        ticket = baker.make(Ticket, user=user)

        data = api_client.get('/api/tickets/').json()

        assert len(data) == 1
        assert data[0]['buyer'] == ticket.buyer

    def test_create(self, api_client, user):
        session = baker.make(Session, user=user)

        r = api_client.post('/api/tickets/', {
            'session': session.id,
            'seat': 5,
            'buyer': 'Иванов Иван',
            'price': 300,
        })

        ticket = Ticket.objects.get(id=r.json()['id'])
        assert ticket.seat == 5
        assert ticket.buyer == 'Иванов Иван'

    def test_delete(self, api_client, user, otp):
        tickets = baker.make(Ticket, user=user, _quantity=10)

        api_client.delete(f'/api/tickets/{tickets[0].id}/')

        data = api_client.get('/api/tickets/').json()
        assert len(data) == 9

    def test_update(self, api_client, user, otp):
        ticket = baker.make(Ticket, user=user)

        api_client.put(f'/api/tickets/{ticket.id}/', {
            'session': ticket.session.id,
            'seat': 10,
            'buyer': 'Петров Пётр',
            'price': 500,
        })

        ticket.refresh_from_db()
        assert ticket.seat == 10


@pytest.mark.django_db
class TestAccess:
    def test_only_own_data(self, api_client, user):
        baker.make(Genre, user=user, _quantity=3)
        baker.make(Genre, user=baker.make(User), _quantity=5)

        data = api_client.get('/api/genres/').json()
        assert len(data) == 3

    def test_update_and_delete_without_otp(self, api_client, user):
        genre = baker.make(Genre, user=user)

        r = api_client.put(f'/api/genres/{genre.id}/', {'name': 'Драма'})
        assert r.status_code == 403

        r = api_client.delete(f'/api/genres/{genre.id}/')
        assert r.status_code == 403

    def test_otp_login(self, api_client):
        key = api_client.get('/api/user/otp-qr/').json()['key']

        r = api_client.post('/api/user/otp-login/', {'key': pyotp.TOTP(key).now()})
        assert r.json()['success'] is True

        r = api_client.get('/api/user/otp-status/')
        assert r.json()['otp_good'] is True
