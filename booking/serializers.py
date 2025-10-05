# booking/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Movie, Show, Booking

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = User(username=validated_data["username"], email=validated_data.get("email", ""))
        user.set_password(validated_data["password"])
        user.save()
        return user


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ("id", "title", "duration_minutes", "synopsis")


class ShowSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Show
        fields = ("id", "movie", "screen_name", "date_time", "total_seats")


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    show = ShowSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ("id", "user", "show", "seat_number", "status", "created_at")
        read_only_fields = ("id", "user", "status", "created_at", "show")


class BookSeatSerializer(serializers.Serializer):
    seat_number = serializers.IntegerField(min_value=1)
