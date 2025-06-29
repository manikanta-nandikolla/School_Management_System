from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from teachers.models import Attendance, Mark, LeaveRequest, Exam
from headmaster.models import ExamSchedule
from .forms import LeaveRequestForm
from accountant.models import StudentFee
from django.conf import settings
from django.contrib import messages
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import json
from django.template.loader import get_template
from xhtml2pdf import pisa
from weasyprint import HTML
from accounts.models import CustomUser
from django.core.mail import send_mail, EmailMessage
from collections import defaultdict
from django.db.models import Avg, Count, Q, Sum
from datetime import date
from django.templatetags.static import static
from accountant.utils import generate_receipt_pdf_weasyprint
from django.template.loader import render_to_string
import logging
from django.utils import timezone
import io

logger = logging.getLogger(__name__)
# Create your views here.

@login_required
def student_dashboard(request):
    user = request.user
    if user.role != 'student':
        return redirect('login')

    # Attendance
    attendance = Attendance.objects.filter(student=user)
    total_days = attendance.count()
    present_days = attendance.filter(status='Present').count()
    absent_days = total_days - present_days
    attendance_percent = round((present_days / total_days) * 100, 2) if total_days > 0 else 0

    # Low attendance alert
    if attendance_percent < 75:
        send_mail(
            subject="⚠️ Low Attendance Alert",
            message=f"Dear {user.get_full_name()},\n\nYour attendance is currently {attendance_percent}%. Please improve your attendance.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

    # Marks
    marks = Mark.objects.filter(student=user).select_related('subject', 'exam')

    # Grouped marks for table display
    grouped_marks = defaultdict(list)
    for mark in marks:
        grouped_marks[mark.exam.name].append(mark)

    # Chart data: exam-subject label, value, color
    chart_labels = []
    chart_values = []
    chart_colors = []

    EXAM_COLORS = [
        "#4caf50",  # Green
        "#2196f3",  # Blue
        "#ff9800",  # Orange
        "#9c27b0",  # Purple
        "#f44336",  # Red
        "#3f51b5",  # Indigo
        "#00bcd4",  # Cyan
        "#cddc39",  # Lime
        "#607d8b",  # Blue Grey
    ]

    exam_color_map = {}
    color_index = 0

    for mark in marks:
        exam_name = mark.exam.name
        subject_name = mark.subject.name
        label = f"{exam_name} - {subject_name}"

        chart_labels.append(label)
        chart_values.append(mark.marks_obtained)

        if exam_name not in exam_color_map:
            exam_color_map[exam_name] = EXAM_COLORS[color_index % len(EXAM_COLORS)]
            color_index += 1

        chart_colors.append(exam_color_map[exam_name])

    # Leave
    leave_requests = LeaveRequest.objects.filter(student=user)
    form = LeaveRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        leave = form.save(commit=False)
        leave.student = user
        leave.save()
        return redirect('student_dashboard')

    # Upcoming exams
    upcoming_exams = ExamSchedule.objects.filter(
        exam_date__gte=timezone.now().date(),
        class_section=user.class_section
    ).order_by("exam_date", "exam_time")

    context = {
        'attendance': attendance,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percent': attendance_percent,

        'marks': marks,
        'grouped_marks': dict(grouped_marks),

        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'chart_colors': json.dumps(chart_colors),

        'leave_requests': leave_requests,
        'form': form,
        'class_section': user.class_section.class_name if user.class_section else 'Not Assigned',
        'upcoming_exams': upcoming_exams,
    }

    return render(request, 'students/dashboard.html', context)

@login_required
def generate_report_card_pdf(request):
    user = request.user

    if user.role != 'student':
        return redirect('login')

    # Attendance
    attendance = Attendance.objects.filter(student=user)
    total_days = attendance.count()
    present_days = attendance.filter(status='Present').count()
    absent_days = total_days - present_days
    attendance_percent = round((present_days / total_days) * 100, 2) if total_days > 0 else 0

    # Marks
    marks = Mark.objects.filter(student=user)
    grouped_marks = defaultdict(list)
    for mark in marks:
        grouped_marks[mark.exam.name].append(mark)

    # Subject-wise average
    subject_avg = {}
    all_subjects = (
        Mark.objects
        .filter(student__class_section=user.class_section)
        .values('subject__name')
        .annotate(avg=Avg('marks_obtained'))
    )
    
    def get_grade_and_remark(score):
        if score >= 90:
            return 'O', 'Outstanding'
        elif score >= 80:
            return 'S', 'Super'
        elif score >= 70:
            return 'A', 'Excellent'
        elif score >= 60:
            return 'B', 'Good'
        elif score >= 50:
            return 'C', 'Satisfactory'
        elif score >= 40:
            return 'D', 'Needs Improvement'
        else:
            return 'F', 'Fail'

    total_score = 0
    mark_count = 0

    for mark in marks:
        subject_name = mark.subject.name
        avg = subject_avg.get(subject_name)
        mark.subject_avg = f"{avg:.2f}" if avg is not None else "N/A"

        grade, remark = get_grade_and_remark(mark.marks_obtained)
        mark.grade = grade
        mark.remark = remark

        total_score += mark.marks_obtained
        mark_count += 1

    gpa = round(total_score / mark_count, 2) if mark_count > 0 else "N/A"
    
    for subject in all_subjects:
        subject_avg[subject['subject__name']] = subject['avg']

    # Attach formatted avg
    for mark in marks:
        subject_name = mark.subject.name
        avg = subject_avg.get(subject_name)
        mark.subject_avg = f"{avg:.2f}" if avg is not None else "N/A"

    # Context
    context = {
        'student': user,
        'attendance': attendance,
        'marks': marks,
        'grouped_marks': dict(grouped_marks),
        'attendance_percent': attendance_percent,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'current_date': date.today().strftime('%B %d, %Y'),
        'school_logo_url': request.build_absolute_uri(static('images/logo.jpeg')),
        'gpa':gpa,  
    }

    # Render HTML
    html_string = render_to_string('students/report_card_pdf.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))

    # Generate PDF
    pdf_file = html.write_pdf()

    # Return PDF response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report_card.pdf"'
    return response

@login_required
def my_pending_fees(request):
    if request.user.role != 'student':
        return redirect('student_login')

    pending_fees = StudentFee.objects.filter(student=request.user, status='unpaid')
    return render(request, 'student/pending_fees.html', {'pending_fees': pending_fees})

@login_required
def my_fee_receipts(request):
    if request.user.role != 'student':
        return redirect('student_login')

    paid_fees = StudentFee.objects.filter(student=request.user, status='paid')
    return render(request, 'students/fee_receipt.html', {'paid_fees': paid_fees})

@login_required
def student_fee_payment(request):
    if request.user.role != 'student':
        return redirect('student_login')

    unpaid_fee = StudentFee.objects.filter(student=request.user, status='unpaid').first()

    if not unpaid_fee:
        return render(request, 'students/fee_pay.html', {'message': 'No pending fee.'})

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        'amount': int(unpaid_fee.amount * 100),
        'currency': 'INR',
        'payment_capture': '1'
    })

    unpaid_fee.razorpay_order_id = payment['id']
    unpaid_fee.save()

    return render(request, 'students/fee_pay.html', {
        'fee': unpaid_fee,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'order_id': payment['id'],
    })


@csrf_exempt
def razorpay_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            if data.get("event") == "payment.captured":
                order_id = data["payload"]["payment"]["entity"]["order_id"]
                fee = StudentFee.objects.get(razorpay_order_id=order_id)
                fee.status = 'paid'
                fee.save()

                # Generate PDF receipt
                generate_receipt_pdf_weasyprint(fee)

                # Email receipt
                if fee.receipt_pdf:
                    email = EmailMessage(
                        subject="📄 Fee Receipt",
                        body=f"Dear {fee.student.get_full_name()},\n\nThank you for paying ₹{fee.amount}. Receipt attached.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[fee.student.email],
                    )
                    email.attach_file(fee.receipt_pdf.path)
                    email.send()

                # Notify accountant(s)
                from accounts.models import CustomUser
                accountants = CustomUser.objects.filter(role='accountant')
                for acc in accountants:
                    send_mail(
                        subject="📥 Fee Payment Received",
                        message=f"{fee.student.get_full_name()} paid ₹{fee.amount}.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[acc.email],
                    )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'invalid'}, status=400)

@login_required
def payment_success(request, fee_id):
    fee = get_object_or_404(StudentFee, id=fee_id)

    if request.user != fee.student:
        messages.error(request, "You are not authorized to view this payment.")
        return redirect('student_dashboard')

    if fee.status != 'paid':
        # Show "processing payment" page
        return render(request, 'students/payment_pending.html', {'fee': fee})

    return render(request, 'students/payment_success.html', {'fee': fee})


@login_required
def download_fee_receipt(request, fee_id):
    fee = get_object_or_404(StudentFee, id=fee_id, student=request.user, status='paid')

    template_path = 'students/receipt_pdf.html'
    context = {'fee': fee}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receipt_{fee.id}.pdf'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('UTF-8')), dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating receipt')
    return response


@login_required
def fee_history(request):
    student = request.user
    fee_records = StudentFee.objects.filter(student=student).order_by('-date', '-id')

    return render(request, 'students/fee_history.html', {
        'fee_records': fee_records
    })
    
def send_fee_receipt_email(fee):
    if not fee.receipt_pdf:
        return

    subject = "📄 Your Fee Payment Receipt"
    message = f"Dear {fee.student.get_full_name()},\n\nThank you for your payment of ₹{fee.amount}.\nPlease find your receipt attached.\n\nRegards,\nAdmin"
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[fee.student.email],
    )
    email.attach_file(fee.receipt_pdf.path)
    email.send()