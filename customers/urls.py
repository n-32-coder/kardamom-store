from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path

from . import views


def logout_get(request):
    logout(request)
    return redirect('home')


urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='customers/login.html'), name='login'),
    path('logout/', logout_get, name='logout'),
]
