# collecte/urls.py

from django.urls import path
from . import views

app_name = 'collecte'  # Définition du namespace pour l'application 'collecte'

urlpatterns = [
    path('', views.home, name='home'),  
    path('reset/', views.empty_sql, name='empty_sql'),  
    path('graphiques/', views.graphiques, name='graphiques'),  # Ajout de l'URL pour les graphiques
]

