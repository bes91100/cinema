from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cinema.api import (
    GenresViewset,
    HallsViewset,
    MoviePhotosViewset,
    MoviesViewset,
    SessionsViewset,
    TicketsViewset,
    UserViewset,
)

router = DefaultRouter()
router.register("genres", GenresViewset, basename="genres")
router.register("movies", MoviesViewset, basename="movies")
router.register("movie-photos", MoviePhotosViewset, basename="movie-photos")
router.register("halls", HallsViewset, basename="halls")
router.register("sessions", SessionsViewset, basename="sessions")
router.register("tickets", TicketsViewset, basename="tickets")
router.register("user", UserViewset, basename="user")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
