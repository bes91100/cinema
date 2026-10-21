from rest_framework import serializers

from cinema.models import Genre, Hall, Movie, MoviePhoto, Session, Ticket


class UserDataSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    def create(self, validated_data):
        if 'request' in self.context:
            validated_data['user'] = self.context['request'].user

        return super().create(validated_data)


class GenreSerializer(UserDataSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'user']


class MovieSerializer(UserDataSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'year', 'duration', 'genre', 'picture', 'user']


class MoviePhotoSerializer(UserDataSerializer):
    class Meta:
        model = MoviePhoto
        fields = ['id', 'movie', 'picture', 'user']


class HallSerializer(UserDataSerializer):
    class Meta:
        model = Hall
        fields = ['id', 'name', 'capacity', 'picture', 'user']


class SessionSerializer(UserDataSerializer):
    class Meta:
        model = Session
        fields = ['id', 'movie', 'hall', 'start', 'price', 'user']


class TicketSerializer(UserDataSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'session', 'seat', 'buyer', 'price', 'user']
