from django.urls import path
from .views import post, login, index, stream

urlpatterns = [
    path('django/post', post),
    path('django/login', login),
    path('django', index),
    path('django/stream', stream)
]
