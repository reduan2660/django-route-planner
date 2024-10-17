from django.urls import path

from . import views

urlpatterns = [
    # path("api", views.get_optimal_route, name="route"),
    path('api/', views.get_optimal_route, name='get_optimal_route'),
    path("proxy-google-maps/", views.proxy_google_maps, name="proxy_google_maps"),
    path("", views.index, name="index"),
]