import base64, os
import qrcode
from io import BytesIO
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.files.base import ContentFile
from django.conf import settings
from .models import StudentFee, TeacherSalary
from django.db.models import Max

def generate_qr_code_base64(data: str) -> str:
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def get_logo_base64(filename="logo.jpeg"):
    path = os.path.join(settings.BASE_DIR, "static", "images", filename)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"

def generate_receipt_pdf_weasyprint(fee):
   
    if not fee.receipt_number:
        last = StudentFee.objects.aggregate(Max('receipt_number'))['receipt_number__max'] or 0
        fee.receipt_number = last + 1
        fee.save()

    qr_data = f"Txn ID: {fee.razorpay_order_id or 'N/A'} - ₹{fee.amount} - {fee.date}"
    qr_base64 = generate_qr_code_base64(qr_data)
    qr_code_uri = f"data:image/png;base64,{qr_base64}"

    html_string = render_to_string("students/receipt_template.html", {
        "fee": fee,
        "logo_url": get_logo_base64("logo.jpeg"),
        "signature_url": get_logo_base64("signature.jpeg"),
        "qr_code": qr_code_uri,
    })

    html = HTML(string=html_string)
    result = BytesIO()
    html.write_pdf(result)

    fee.receipt_pdf.save(f"receipt_{fee.id}.pdf", ContentFile(result.getvalue()), save=True)


def generate_payslip_pdf_weasyprint(salary):
    if not salary.payslip_number:
        last_num = TeacherSalary.objects.aggregate(Max('payslip_number'))['payslip_number__max'] or 0
        salary.payslip_number = last_num + 1
        salary.save()

    # Construct QR code with proper prefix
    qr_data = f"{salary.teacher.get_full_name()} - ₹{salary.amount} - {salary.month}, {salary.year}"
    qr_base64 = generate_qr_code_base64(qr_data)
    qr_code_uri = f"data:image/png;base64,{qr_base64}"

    context = {
        "salary": salary,
        "logo_url": get_logo_base64("logo.jpeg"),
        "signature_url": get_logo_base64("signature.jpeg"),
        "qr_code": qr_code_uri,
    }

    html = render_to_string("accountant/payslip_template.html", context)
    result = BytesIO()
    HTML(string=html).write_pdf(result)
    filename = f"payslip_{salary.id}.pdf"
    salary.payslip.save(filename, ContentFile(result.getvalue()), save=True)