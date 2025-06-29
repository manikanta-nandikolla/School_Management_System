# students/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('report-card/', views.generate_report_card_pdf, name='generate_report_card_pdf'),
    path('pending-fees/', views.my_pending_fees, name='my_pending_fees'),
    path('receipts/', views.my_fee_receipts, name='my_fee_receipts'),
    path('fee-payment/', views.student_fee_payment, name='student_fee_payment'),
    path('razorpay/webhook/', views.razorpay_webhook, name='razorpay_webhook'),
    path('payment-success/<int:fee_id>/', views.payment_success, name='payment_success'),
    path('fee-history/', views.fee_history, name='student_fee_history'),
    path('fee-receipt/<int:fee_id>/pdf/', views.download_fee_receipt, name='download_fee_receipt'),
]