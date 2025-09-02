from django.urls import path
from . import views

app_name = 'matches'

urlpatterns = [
    path('connections/<str:user_email>/', views.get_user_connections, name='user-connections'),
]
