from django.urls import path
from . import views

urlpatterns = [
    path("get-book-details/<int:book_id>/", views.get_book_details, name="get_book_details",),
]