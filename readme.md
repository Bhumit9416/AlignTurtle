# Movie Ticket Booking - Backend

## Tech stack
- Python 3.10+
- Django 4.x
- Django REST Framework
- djangorestframework-simplejwt (JWT)
- drf-yasg (Swagger)

## Setup (local)
1. Clone repo
2. python -m venv venv
3. source venv/Scripts/activate
4. pip install -r requirements.txt
5. python manage.py migrate
6. python manage.py createsuperuser
7. python manage.py runserver
8. Open http://127.0.0.1:8000/swagger/ for API docs

## JWT
- POST /signup/ to register
- POST /login/ to obtain JWT (`access` token)
- Add header `Authorization: Bearer <access_token>` to protected endpoints

## Endpoints
- POST /signup/
- POST /login/
- GET /movies/
- GET /movies/<id>/shows/
- POST /shows/<id>/book/  (body: {"seat_number": <int>})
- POST /bookings/<id>/cancel/
- GET /my-bookings/
- Swagger: /swagger/

## Business rules implemented
- Prevent double booking (checks existing bookings with status='booked')
- Prevent overbooking (checks booked count against `total_seats`)
- Cancelling booking sets `status='cancelled'`, freeing seat

## Notes & bonus
- Booking uses DB transaction + `select_for_update()` to reduce race conditions.
- Permission check prevents cancelling others' bookings.

