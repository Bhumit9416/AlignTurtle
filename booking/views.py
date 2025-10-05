# booking/views.py
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Movie, Show, Booking
from .serializers import (
    SignupSerializer, MovieSerializer, ShowSerializer,
    BookingSerializer, BookSeatSerializer
)
from .permissions import IsOwnerOrReadOnly

# Signup
class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]


# List all movies
class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]


# Shows for a movie
class MovieShowsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        shows = movie.shows.all()
        serializer = ShowSerializer(shows, many=True)
        return Response(serializer.data)


# Book a seat for a show
class BookSeatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        serializer = BookSeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seat_number = serializer.validated_data["seat_number"]

        show = get_object_or_404(Show, pk=id)

        if seat_number > show.total_seats:
            return Response({"detail": "Seat number out of range."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # lock the show row to reduce race conditions
                show_locked = Show.objects.select_for_update().get(pk=show.pk)

                # check overbooking
                booked_count = Booking.objects.filter(show=show_locked, status=Booking.STATUS_BOOKED).count()
                if booked_count >= show_locked.total_seats:
                    return Response({"detail": "Show is fully booked."}, status=status.HTTP_400_BAD_REQUEST)

                # check seat double-booking
                seat_taken = Booking.objects.filter(show=show_locked, seat_number=seat_number, status=Booking.STATUS_BOOKED).exists()
                if seat_taken:
                    return Response({"detail": "Seat already booked."}, status=status.HTTP_400_BAD_REQUEST)

                booking = Booking.objects.create(
                    user=request.user,
                    show=show_locked,
                    seat_number=seat_number,
                    status=Booking.STATUS_BOOKED
                )
                out = BookingSerializer(booking)
                return Response(out.data, status=status.HTTP_201_CREATED)
        except Show.DoesNotExist:
            return Response({"detail": "Show not found."}, status=status.HTTP_404_NOT_FOUND)


# Cancel booking
class CancelBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def post(self, request, id):
        booking = get_object_or_404(Booking, pk=id)
        # permission check
        if booking.user != request.user:
            return Response({"detail": "You cannot cancel someone else's booking."}, status=status.HTTP_403_FORBIDDEN)
        if booking.status == Booking.STATUS_CANCELLED:
            return Response({"detail": "Booking already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            booking.status = Booking.STATUS_CANCELLED
            booking.save()
        return Response({"detail": "Booking cancelled successfully."}, status=status.HTTP_200_OK)


# List current user's bookings
class MyBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by("-created_at")
