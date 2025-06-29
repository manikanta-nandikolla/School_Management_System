from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.accountant_dashboard, name='accountant_dashboard'),
    # Student Fee
    path('fees/', views.student_fee_list, name='student_fee_list'),
    path('fees/add/', views.student_fee_create, name='student_fee_create'),
    path('fees/receive/<int:fee_id>/', views.receive_student_fee, name='receive_student_fee'),
    path('fees/edit/<int:pk>/', views.student_fee_update, name='student_fee_update'),
    path('fees/delete/<int:pk>/', views.student_fee_delete, name='student_fee_delete'),
    path('webhook/', views.student_fee_list, name='student_fee_list'),
    path('student-fees/<int:fee_id>/receipt/', views.view_fee_receipt, name='view_fee_receipt'),
    path('export-fees/', views.export_fees_excel, name='export_fees_excel'),

    # Teacher Salary
    path('salaries/', views.teacher_salary_list, name='teacher_salary_list'),
    path('salaries/add/', views.teacher_salary_create, name='teacher_salary_create'),
    path('salaries/edit/<int:pk>/', views.teacher_salary_update, name='teacher_salary_update'),
    path('salaries/delete/<int:pk>/', views.teacher_salary_delete, name='teacher_salary_delete'),
    path('accountant/pay-teacher-salary/', views.pay_teacher_salary, name='pay_teacher_salary'),
    path('teacher-salary/pay/<int:salary_id>/', views.initiate_teacher_salary_payment, name='initiate_teacher_salary_payment'),
    path('teacher-salary/payment-success/', views.teacher_salary_payment_success, name='teacher_salary_payment_success'),
    path('teacher/salary/<int:pk>/download/', views.download_teacher_payslip, name='download_teacher_payslip'),
    path('export-teacher-salary-excel', views.export_teacher_salaries_excel, name="export_teacher_salaries_excel"),
]
