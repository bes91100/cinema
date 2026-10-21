import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from cinema.models import Genre, Hall, Movie, Session, Ticket


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        user = User.objects.filter(is_superuser=True).first()

        genres = []
        for name in ['Комедия', 'Драма', 'Боевик', 'Ужасы', 'Фантастика', 'Мультфильм']:
            genres.append(Genre.objects.create(name=name, user=user))

        halls = []
        for i in range(1, 11):
            halls.append(Hall.objects.create(name=f'Зал {i}', capacity=random.randint(30, 300), user=user))

        movies = []
        for _ in range(1000):
            movies.append(Movie.objects.create(
                title=fake.sentence(nb_words=3),
                year=random.randint(1960, 2026),
                duration=random.randint(70, 180),
                genre=random.choice(genres),
                user=user,
            ))

        sessions = []
        for _ in range(1000):
            sessions.append(Session.objects.create(
                movie=random.choice(movies),
                hall=random.choice(halls),
                start=fake.date_time_between(start_date='-30d', end_date='+30d'),
                price=random.randint(200, 800),
                user=user,
            ))

        for _ in range(1000):
            Ticket.objects.create(
                session=random.choice(sessions),
                seat=random.randint(1, 100),
                buyer=fake.name(),
                price=random.randint(200, 800),
                user=user,
            )
