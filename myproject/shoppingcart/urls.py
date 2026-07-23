from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart),
    path('get-cart/', views.get_cart_view, name='get_shopping_cart'),
    path('remove-from-cart/', views.remove_from_cart, name = 'remove_from_cart'),
    path('remove-cart/', views.removeCart, name = "removeCart"),
    path('create-cart/', views.createCart, name = "createCart"),
    path('get-all-books/', views.getAllBooksAvailable, name = "getAllBooks"),
    path('add-book/', views.addBookToCart, name = "addBook")
]