from django.urls import path

from . import views

urlpatterns = [
    path('Test/GetStringGetMethod', views.GetStringGetMethod, name='GetStringGetMethod'),
    path('Test/', views.index, name='index'),
]