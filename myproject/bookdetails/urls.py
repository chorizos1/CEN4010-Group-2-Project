from django.urls import path
from . import views

urlpatterns = [
    path("get-book-details/<int:book_id>/", views.get_book_details, name="get_book_details",),
    path("create-book/", views.create_book, name="create_book",),
    path("create-author/", views.create_author, name="create_author"),
]