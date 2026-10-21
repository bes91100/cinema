import base64
import io

import pyotp
import qrcode
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Avg, Count, Max, Min, Sum
from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cinema.models import Genre, Hall, Movie, MoviePhoto, Session, Ticket, UserProfile
from cinema.serializers import (
    GenreSerializer,
    HallSerializer,
    MoviePhotoSerializer,
    MovieSerializer,
    SessionSerializer,
    TicketSerializer,
)


class OTPRequired(BasePermission):
    def has_permission(self, request, view):
        return bool(cache.get(f'otp_good_{request.user.id}', False))


class UserDataViewset(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    def get_queryset(self):
        qs = super().get_queryset()

        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)

        return qs

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), OTPRequired()]

        return super().get_permissions()


class GenresViewset(UserDataViewset):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filterset_fields = {
        'name': ['icontains'],
        'user': ['exact'],
    }

    @action(detail=False, methods=['GET'])
    def stats(self, request, *args, **kwargs):
        return Response(self.get_queryset().aggregate(
            count=Count('id'),
        ))


class MoviesViewset(UserDataViewset):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filterset_fields = {
        'title': ['icontains'],
        'year': ['exact'],
        'duration': ['exact'],
        'genre': ['exact'],
        'user': ['exact'],
    }

    @action(detail=False, methods=['GET'])
    def stats(self, request, *args, **kwargs):
        return Response(self.get_queryset().aggregate(
            count=Count('id'),
            avg_year=Avg('year'),
            min_year=Min('year'),
            max_year=Max('year'),
            avg_duration=Avg('duration'),
        ))

    @action(detail=False, methods=['GET'])
    def export(self, request, *args, **kwargs):
        wb = Workbook()
        ws = wb.active
        ws.append(['ID', 'Название', 'Год', 'Длительность', 'Жанр'])

        for movie in self.get_queryset():
            ws.append([movie.id, movie.title, movie.year, movie.duration, movie.genre.name if movie.genre else ''])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="movies.xlsx"'
        wb.save(response)
        return response


class MoviePhotosViewset(UserDataViewset):
    queryset = MoviePhoto.objects.all()
    serializer_class = MoviePhotoSerializer
    filterset_fields = ['movie']

    @action(detail=False, methods=['GET'])
    def stats(self, request, *args, **kwargs):
        return Response(self.get_queryset().aggregate(
            count=Count('id'),
        ))


class HallsViewset(UserDataViewset):
    queryset = Hall.objects.all()
    serializer_class = HallSerializer
    filterset_fields = {
        'name': ['icontains'],
        'capacity': ['exact'],
        'user': ['exact'],
    }

    @action(detail=False, methods=['GET'])
    def stats(self, request, *args, **kwargs):
        return Response(self.get_queryset().aggregate(
            count=Count('id'),
            avg_capacity=Avg('capacity'),
            max_capacity=Max('capacity'),
            sum_capacity=Sum('capacity'),
        ))


class SessionsViewset(UserDataViewset):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filterset_fields = {
        'movie': ['exact'],
        'hall': ['exact'],
        'start': ['date'],
        'price': ['exact'],
        'user': ['exact'],
    }

    @action(detail=False, methods=['GET'])
    def stats(self, request, *args, **kwargs):
        return Response(self.get_queryset().aggregate(
            count=Count('id'),
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
        ))


class TicketsViewset(UserDataViewset):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    filterset_fields = {
        'session': ['exact'],
        'seat': ['exact'],
        'buyer': ['icontains'],
        'price': ['exact'],
        'user': ['exact'],
    }

    @action(detail=False, methods=['GET'])
    def stats(self, request, *args, **kwargs):
        return Response(self.get_queryset().aggregate(
            count=Count('id'),
            sum_price=Sum('price'),
            avg_price=Avg('price'),
        ))


class UserViewset(GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'], permission_classes=[])
    def info(self, request, *args, **kwargs):
        return Response({
            'is_authenticated': request.user.is_authenticated,
            'username': request.user.username,
            'is_superuser': request.user.is_superuser,
        })

    @action(detail=False, methods=['POST'], permission_classes=[], url_path='login')
    def use_login(self, request, *args, **kwargs):
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        if user:
            login(request, user)

        return Response({
            'is_authenticated': bool(user)
        })

    @action(detail=False, methods=['POST'], url_path='logout')
    def use_logout(self, request, *args, **kwargs):
        logout(request)
        return Response({})

    @action(detail=False, methods=['GET'], permission_classes=[IsAdminUser])
    def users(self, request, *args, **kwargs):
        return Response(list(User.objects.values('id', 'username')))

    def get_otp_key(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={'otp_key': pyotp.random_base32()},
        )
        return profile.otp_key

    @action(detail=False, methods=['GET'], url_path='otp-qr')
    def otp_qr(self, request, *args, **kwargs):
        key = self.get_otp_key()
        uri = pyotp.TOTP(key).provisioning_uri(name=request.user.username, issuer_name='Кинотеатр')

        buffer = io.BytesIO()
        qrcode.make(uri).save(buffer, format='PNG')

        return Response({
            'key': key,
            'qr': 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode(),
        })

    @action(detail=False, methods=['POST'], url_path='otp-login')
    def otp_login(self, request, *args, **kwargs):
        totp = pyotp.TOTP(self.get_otp_key())

        success = False
        if totp.verify(str(request.data.get('key'))):
            cache.set(f'otp_good_{request.user.id}', True, settings.OTP_LIFETIME)
            success = True

        return Response({
            'success': success
        })

    @action(detail=False, methods=['GET'], url_path='otp-status')
    def otp_status(self, request, *args, **kwargs):
        return Response({
            'otp_good': cache.get(f'otp_good_{request.user.id}', False)
        })
