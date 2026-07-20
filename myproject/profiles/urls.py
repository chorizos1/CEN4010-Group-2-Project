from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_profile_view, name='get_profile'),
    path('create/', views.create_profile_view, name='create_profile'),
    path('preferences/', views.update_preferences_view, name='update_preferences'),
    path('email/', views.update_email_view, name='update_email'),
    path('password/', views.change_password_view, name='change_password'),
]
