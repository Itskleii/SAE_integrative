# collecte/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Page d'accueil avec tous les capteurs et leurs données
]
