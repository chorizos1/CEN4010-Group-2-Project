from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart),
    path('get-cart/', views.get_cart_view, name='get_shopping_cart')
    
]