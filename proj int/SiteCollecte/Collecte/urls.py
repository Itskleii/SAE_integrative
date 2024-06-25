# collecte/urls.py

from django.urls import path
from . import views

app_name = 'collecte'  # Définition du namespace pour l'application 'collecte'

urlpatterns = [
    path('', views.home, name='home'),  
    path('reset/', views.empty_sql, name='empty_sql'),  
    path("graphiques.html/", views.indexgraph),
    path('api/all-sensor-data/', views.get_all_sensor_data, name='get_all_sensor_data'),
    path('update_sensor/<str:sensor_id>/', views.update_sensor, name='update_sensor'),
    path('view_sensor/<str:sensor_id>/', views.view_sensor, name='view_sensor'),]

