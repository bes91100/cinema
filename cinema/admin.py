from django.contrib import admin

from cinema.models import Genre, Hall, Movie, MoviePhoto, Session, Ticket, UserProfile


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'year', 'duration', 'genre', 'user']


@admin.register(MoviePhoto)
class MoviePhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'movie', 'picture', 'user']


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'capacity', 'user']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'movie', 'hall', 'start', 'price', 'user']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'seat', 'buyer', 'price', 'user']
