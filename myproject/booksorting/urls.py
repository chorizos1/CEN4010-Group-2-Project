from django.urls import path

from . import views

urlpatterns = [
    path("books/genre", views.books_by_genre, name="books_by_genre"),
    path("books/topsellers", views.top_sellers, name="top_sellers"),
    path("books/rating", views.books_by_min_rating, name="books_by_min_rating"),
    path("books/discount", views.apply_discount, name="apply_discount"),
]
