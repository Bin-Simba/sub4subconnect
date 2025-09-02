from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.get_user_profile, name='profile'),
    path('profile/update/', views.update_user_profile, name='profile-update'),
    path('users-with-youtube/', views.get_users_with_youtube, name='users-with-youtube'),
    path('youtube-proxy/', views.youtube_api_proxy, name='youtube-proxy'),
    path('explore/', views.explore_users, name='explore'),
    path('update-youtube-data/', views.update_youtube_data, name='update-youtube-data'),
]
