from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cars/', views.cars, name='cars'),
    path('cars/<slug:slug>/', views.car_detail_view, name='car_detail'),
    path('contacts/', views.contacts, name='contacts'),
]