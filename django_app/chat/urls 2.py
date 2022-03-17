from django.urls import path
from .views import post, login, index, stream

urlpatterns = [
    path('post', post),
    path('login/', login),
    path('', index),
    path('stream', stream)
]
