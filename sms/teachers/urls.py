from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('record_attendance/', views.record_attendance, name='record_attendance'),
    path('leave_approval/', views.leave_approval_view, name='leave_approval'),
    path('pay_slips/', views.teacher_salary_view, name='teacher_salary_view'),
    path('salary-slips/', views.view_salary_records, name='view_salary_slips'),
    path('my-salary/', views.my_salary_records, name='my_salary_records'),
    path('add-marks/', views.add_marks, name='add_marks'),
    path('my-payslips/', views.my_payslips, name='my_payslips'),
    path('my-payslips/<int:pk>/download/', views.download_payslip, name='download_payslip'),
]
