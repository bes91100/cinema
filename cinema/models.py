from django.contrib.auth.models import User
from django.db import models


class Genre(models.Model):
    name = models.TextField("Название")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.TextField("Название")
    year = models.IntegerField("Год")
    duration = models.IntegerField("Длительность, мин")
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE, null=True)
    picture = models.ImageField("Постер", null=True, upload_to="movies")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return self.title


class MoviePhoto(models.Model):
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE)
    picture = models.ImageField("Фото", upload_to="movie_photos")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Фото фильма"
        verbose_name_plural = "Фото фильмов"


class Hall(models.Model):
    name = models.TextField("Название")
    capacity = models.IntegerField("Вместимость")
    picture = models.ImageField("Фото", null=True, upload_to="halls")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"

    def __str__(self):
        return self.name


class Session(models.Model):
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE)
    hall = models.ForeignKey("Hall", on_delete=models.CASCADE)
    start = models.DateTimeField("Начало")
    price = models.IntegerField("Цена")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Сеанс"
        verbose_name_plural = "Сеансы"

    def __str__(self):
        return f"{self.movie} {self.start}"


class Ticket(models.Model):
    session = models.ForeignKey("Session", on_delete=models.CASCADE)
    seat = models.IntegerField("Место")
    buyer = models.TextField("Покупатель")
    price = models.IntegerField("Цена")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_key = models.TextField()
