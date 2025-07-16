from django.urls import path
from . import views

urlpatterns = [
    path('users', views.create_user),
    path('connections', views.add_connection),
    path('connections/remove', views.remove_connection),
    path('users/<str:str_id>/friends', views.list_friends),
    path('users/<str:str_id>/friends-of-friends', views.friends_of_friends),
    path('connections/degree', views.degree_of_separation),
]
