from django.urls import path

from . import views

urlpatterns = [
    path('Test/GetStringGetMethod', views.GetStringGetMethod, name='GetStringGetMethod'),
    path('Test/get_synced_data', views.get_synced_data, name='get_synced_data'),

    path('Test/', views.index, name='index'),
    path('data/', views.fetch, name='fetch'),
    path('ipptv2/',views.ipptv2_data,name = "ipptv2"),
    
]

