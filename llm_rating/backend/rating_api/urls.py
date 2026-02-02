from django.urls import path
from . import views

urlpatterns = [
    path('api/predict/', views.predict_rating, name='predict_rating'),
    path('api/health/', views.health_check, name='health_check'),
]
