from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/student/', views.student_login_view, name='student_login'),
    path('register/student/', views.student_register_view, name='student_register'),
    path('teacher/register/', views.teacher_register_view, name='teacher_register'),
    path('teacher/login/', views.teacher_login_view, name='teacher_login'),
    path('logout/', views.logout_view, name='logout'),
    path('headmaster/register/', views.headmaster_register_view, name='headmaster_register'),
    path('headmaster/login/', views.headmaster_login_view, name='headmaster_login'),
    path('principal/login/', views.principal_login_view, name='principal_login'),
    path('accountant/register/', views.accountant_register, name='accountant_register'),
    path('accountant/login/', views.accountant_login, name='accountant_login'),
    
    # Forgot Password URLs
    path("<str:role>/password_reset/", views.password_reset_request, name="password_reset"),
    path("password_reset/done/", views.password_reset_done,    name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("reset/done/", views.password_reset_complete,name="password_reset_complete"),
    path("password_reset/", views.forgot_password_role_selector, name="forgot_password_role_selector"),
]