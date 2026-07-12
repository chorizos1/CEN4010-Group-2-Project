from django.urls import path
from . import views

urlpatterns = [
    path('ratings/', views.create_rating, name='create_rating'),
    path('ratings/<int:book_id>/average/', views.average_rating, name='average_rating'),
    path('comments/', views.create_comment, name='create_comment'),
    path('comments/<int:book_id>/', views.list_comments, name='list_comments'),
]
