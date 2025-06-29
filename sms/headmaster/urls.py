from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.headmaster_dashboard, name='headmaster_dashboard'),
    path('teacher/<int:pk>/', views.view_teacher_profile, name='view_teacher_profile'),
    path('student/<int:pk>/', views.view_student_profile, name='view_student_profile'),
    path('manage-salary/', views.manage_teacher_salary, name='manage_teacher_salary'),
    path('teacher/delete/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('student/delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('headmaster-salaries/', views.headmaster_salary_view, name='headmaster_salary_view'),
    path('assign-class-teacher/', views.assign_class_teacher, name='assign_class_teacher'),
    path('assign-subject-teacher/', views.assign_subject_teacher, name='assign_subject_teacher'),
    path('edit-class-teacher/<int:pk>/', views.edit_class_teacher, name='edit_class_teacher'),
    path('delete-class-teacher/<int:pk>/', views.delete_class_teacher, name='delete_class_teacher'),
    path('edit-subject-teacher/<int:pk>/', views.edit_subject_teacher, name='edit_subject_teacher'),
    path('delete-subject-teacher/<int:pk>/', views.delete_subject_teacher, name='delete_subject_teacher'),    
    path('payslip/view/<int:pk>/', views.view_my_payslip, name='view_my_payslip'),
    path('payslip/download/<int:pk>/', views.download_my_payslip, name='download_my_payslip'),
    path('exams/schedules/', views.schedules_list, name='headmaster_exam_schedules'),
    path('exams/schedules/create/', views.schedule_create, name='headmaster_exam_add'),
    path('exams/schedules/<int:pk>/edit/', views.schedule_update, name='headmaster_exam_edit'),
    path('exams/schedules/<int:pk>/delete/', views.schedule_delete, name='headmaster_exam_delete'),
]

