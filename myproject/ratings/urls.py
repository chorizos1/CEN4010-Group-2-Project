from django.urls import path
from . import views

urlpatterns = [
    # RATINGS
    path('ratings/', views.create_rating, name='create_rating'), # POST
    path('ratings/<int:book_id>/average/', views.average_rating, name='average_rating'), # GET
    path('ratings/<int:rating_id>/', views.rating_detail, name='rating_detail'), # PUT, DELETE [Sprint 4]
    
    # COMMENTS
    # Changed: 'comments/' now handles both GET (list, via ?book_id=) and POST (create) -- previously these were separate paths
    path('comments/', views.comments_collection, name='comments_collection'), # GET, POST
    path('comments/<int:comment_id>/', views.delete_comment, name='delete_comment'), # DELETE [Sprint 4]

]
