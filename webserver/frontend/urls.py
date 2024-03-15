from django.urls import path
from . import views


urlpatterns = [
    path('', views.node_index),
    path('hello/', views.node_hello)
]