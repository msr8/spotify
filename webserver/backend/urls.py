from django.urls import path
from . import views


urlpatterns = [
    path('', views.node_test),
    path('get_nearest_tracks/', views.node_get_nearest_tracks),
    path('get_track_id/', views.node_get_track_id),
    path('test/', views.node_test),
]