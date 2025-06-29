from django.db import models
from accounts.models import CustomUser
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.core.files.base import ContentFile
from io import BytesIO
import qrcode
import base64

User = get_user_model()

# Create your models here.
MONTH_CHOICES = [
    ('Jan', 'January'),
    ('Feb', 'February'),
    ('Mar', 'March'),
    ('Apr', 'April'),
    ('May', 'May'),
    ('Jun', 'June'),
    ('Jul', 'July'),
    ('Aug', 'August'),
    ('Sep', 'September'),
    ('Oct', 'October'),
    ('Nov', 'November'),
    ('Dec', 'December'),
]

PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('razorpay', 'Razorpay'),
    ]
class TeacherSalary(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    basic = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_date = models.DateField()
    note = models.TextField(blank=True, null=True)
    year = models.IntegerField()
    month = models.CharField(max_length=3, choices=MONTH_CHOICES) 
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payslip = models.FileField(upload_to='payslips/', null=True, blank=True)
    payslip_number = models.PositiveIntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.teacher.get_full_name()} - ₹{self.amount} on {self.paid_date}"

    def generate_payslip_pdf(self):
        
        # Generate QR code data
        qr_data = f"{self.teacher.get_full_name()} | ₹{self.amount} | {self.month}, {self.year}"
        qr_img = qrcode.make(qr_data)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Signature file path
        signature_url = '/media/signatures/accountant.png'  # ensure this file exists

        # Render HTML and convert to PDF
        context = {
            'salary': self,
            'teacher': self.teacher,
            'qr_code': qr_base64,
            'signature_url': signature_url,
        }
        html = render_to_string('accountant/payslip_template.html', context)
        pdf_file = BytesIO()
        pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=pdf_file)

        file_name = f'payslip_{self.teacher.id}_{self.month}_{self.year}.pdf'
        self.payslip.save(file_name, ContentFile(pdf_file.getvalue()), save=False)


class StudentFee(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')])
    date = models.DateField(auto_now_add=True)
    receipt_pdf = models.FileField(upload_to='receipts/', null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    receipt_number = models.PositiveIntegerField(null=True, blank=True, unique=True) 

    def __str__(self):
        return f"{self.student.get_full_name()} - ₹{self.amount} - {self.status}"


class PaymentNotification(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_notifications')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.status} - ₹{self.amount}"