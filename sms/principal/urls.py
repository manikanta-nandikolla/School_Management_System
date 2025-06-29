from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.principal_dashboard, name='principal_dashboard'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('export/users/', views.export_users_csv, name='export_users_csv'),
    path('export/users/pdf/', views.export_users_pdf, name='export_users_pdf'),
    path('export/fees/pdf/', views.export_student_fees_pdf, name='export_student_fees_pdf'),
    path('export/salaries/pdf/', views.export_teacher_salaries_pdf, name='export_teacher_salaries_pdf'),
    path('filter/fees/', views.filtered_student_fees, name='filtered_student_fees'),
    path('filter/salaries/', views.filtered_teacher_salaries, name='filtered_teacher_salaries'),

    # Notices
    path('notices/', views.notice_list, name='notice_list'),
    path('notices/create/', views.notice_create, name='notice_create'),
    path('notices/edit/<int:pk>/', views.notice_edit, name='notice_edit'),
    path('notices/delete/<int:pk>/', views.notice_delete, name='notice_delete'),

    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/edit/<int:pk>/', views.event_edit, name='event_edit'),
    path('events/delete/<int:pk>/', views.event_delete, name='event_delete'),

    # Holidays
    path('holidays/', views.holiday_list, name='holiday_list'),
    path('holidays/create/', views.holiday_create, name='holiday_create'),
    path('holidays/edit/<int:pk>/', views.holiday_edit, name='holiday_edit'),
    path('holidays/delete/<int:pk>/', views.holiday_delete, name='holiday_delete'),

]
