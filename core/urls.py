from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/', views.api_root, name='api_root'),
    path('api/health/', views.health_check, name='health_check'),
]