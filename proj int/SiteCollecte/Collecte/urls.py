# collecte/urls.py

from django.urls import path
from . import views

app_name = 'collecte'  # Définition du namespace pour l'application 'collecte'

urlpatterns = [
    path('', views.home, name='home'),  # Page d'accueil avec tous les capteurs et leurs données
]
