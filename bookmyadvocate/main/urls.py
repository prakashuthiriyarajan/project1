"""
Path: bookmyadvocate/main/urls.py
"""

from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Registration
    path('register/client/', views.register_client, name='register_client'),
    path('register/advocate/', views.register_advocate, name='register_advocate'),

    # Login / Logout
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('logout/', views.user_logout, name='logout'),


    # Dashboards
    path('dashboard/client/', views.client_dashboard, name='client_dashboard'),
    path('dashboard/advocate/', views.advocate_dashboard, name='advocate_dashboard'),
]
