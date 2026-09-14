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
    # Password change (logged-in users)
    path('password/', auth_views.PasswordChangeView.as_view(
        template_name='customers/password_change.html',
        success_url='/accounts/password/done/'), name='password_change'),
    path('password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='customers/password_change_done.html'), name='password_change_done'),
    # Password reset (forgot password)
    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='customers/password_reset.html',
        email_template_name='customers/password_reset_email.html',
        subject_template_name='customers/password_reset_subject.txt',
        success_url='/accounts/password/reset/done/'), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='customers/password_reset_done.html'), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='customers/password_reset_confirm.html',
        success_url='/accounts/password/reset/complete/'), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='customers/password_reset_complete.html'), name='password_reset_complete'),
]
