from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from accounts.models import CustomUser
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import CustomUser
from accountant.models import StudentFee, TeacherSalary
from .models import Notice, Event, Holiday
from .forms import NoticeForm, EventForm, HolidayForm
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
import csv
from django.http import HttpResponse
from .utils import render_to_pdf
from django.contrib.auth import get_user_model
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import datetime
from django.template.loader import get_template
from weasyprint import HTML, CSS
from functools import wraps
from django.core.exceptions import PermissionDenied
from io import BytesIO
from django.conf import settings

User = get_user_model()

# Create your views here.
def is_principal(user):
    return user.is_superuser

@login_required
@user_passes_test(lambda u: u.is_superuser)
def principal_dashboard(request):
    students = CustomUser.objects.filter(role='student')
    teachers = CustomUser.objects.filter(role='teacher')
    headmasters = CustomUser.objects.filter(role='headmaster')
    accountants = CustomUser.objects.filter(role='accountant')

    pending_approvals = CustomUser.objects.filter(is_approved=False, is_active=True, is_superuser=False)
    approved_users = CustomUser.objects.filter(is_approved=True, is_superuser=False)
    rejected_users = CustomUser.objects.filter(is_approved=False, is_active=False, is_superuser=False)

    total_fees = StudentFee.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_salaries = TeacherSalary.objects.aggregate(total=Sum('amount'))['total'] or 0

    current_year = timezone.now().year
    
    notices = Notice.objects.order_by('-date_posted')[:5]
    events = Event.objects.filter(event_date__gte=timezone.now().date()).order_by('event_date')[:5]
    holidays = Holiday.objects.filter(holiday_date__gte=timezone.now().date()).order_by('holiday_date')[:5]

    # === Monthly Fee Aggregation ===
    fee_qs = (
        StudentFee.objects
        .filter(status='paid', date__year=current_year)
        .annotate(month_start=TruncMonth('date'))
        .values('month_start')
        .annotate(total=Sum('amount'))
        .order_by('month_start')
    )

    # === Monthly Salary Aggregation ===
    salary_qs = (
        TeacherSalary.objects
        .filter(paid_date__year=current_year)
        .annotate(month_start=TruncMonth('paid_date'))
        .values('month_start')
        .annotate(total=Sum('amount'))
        .order_by('month_start')
    )

    # Convert to chart-ready lists
    def series(qs):
        labels, totals = [], []
        for row in qs:
            labels.append(row['month_start'].strftime('%b'))  # e.g., Jan, Feb
            totals.append(float(row['total'] or 0))
        return labels, totals

    fee_labels, fee_totals = series(fee_qs)
    salary_labels, salary_totals = series(salary_qs)

    context = {
        'students': students,
        'teachers': teachers,
        'headmasters': headmasters,
        'accountants': accountants,
        'pending_approvals': pending_approvals,
        'approved_users': approved_users,
        'rejected_users': rejected_users,
        'notices': notices,
        'events': events,
        'holidays': holidays,
        'total_fees': total_fees,
        'total_salaries': total_salaries,
        'fee_labels': fee_labels,
        'fee_totals': fee_totals,
        'salary_labels': salary_labels,
        'salary_totals': salary_totals,
    }
    return render(request, 'principal/dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def notice_list(request):
    notices = Notice.objects.all().order_by('-date_posted')
    return render(request, 'principal/notice_list.html', {'notices': notices})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def notice_create(request):
    form = NoticeForm(request.POST or None)
    if form.is_valid():
        notice = form.save(commit=False)
        notice.posted_by = request.user
        notice.save()
        messages.success(request, "Notice created successfully.")
        return redirect('notice_list')
    return render(request, 'principal/notice_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def notice_edit(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    form = NoticeForm(request.POST or None, instance=notice)
    if form.is_valid():
        form.save()
        messages.success(request, "Notice updated successfully.")
        return redirect('notice_list')
    return render(request, 'principal/notice_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.delete()
    messages.success(request, "Notice deleted.")
    return redirect('notice_list')

# Repeat for Event
@login_required
@user_passes_test(lambda u: u.is_superuser)
def event_list(request):
    events = Event.objects.all().order_by('event_date')
    return render(request, 'principal/event_list.html', {'events': events})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def event_create(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Event added.")
        return redirect('event_list')
    return render(request, 'principal/event_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, "Event updated.")
        return redirect('event_list')
    return render(request, 'principal/event_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, "Event deleted.")
    return redirect('event_list')

# Repeat for Holiday
@login_required
@user_passes_test(lambda u: u.is_superuser)
def holiday_list(request):
    holidays = Holiday.objects.all().order_by('holiday_date')
    return render(request, 'principal/holiday_list.html', {'holidays': holidays})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def holiday_create(request):
    form = HolidayForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Holiday added.")
        return redirect('holiday_list')
    return render(request, 'principal/holiday_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def holiday_edit(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    form = HolidayForm(request.POST or None, instance=holiday)
    if form.is_valid():
        form.save()
        messages.success(request, "Holiday updated.")
        return redirect('holiday_list')
    return render(request, 'principal/holiday_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def holiday_delete(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    holiday.delete()
    messages.success(request, "Holiday removed.")
    return redirect('holiday_list')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.status = 'approved'
    user.is_approved = True
    user.is_active = True
    user.save()
    send_mail(
        subject="Your Account Has Been Approved",
        message=f"Dear {user.get_full_name()}, your account as a {user.role.title()} has been approved.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    messages.success(request, f"{user.get_full_name()} ({user.role}) has been approved.")
    return redirect('principal_dashboard')
    

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reject_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.status = 'rejected'
    user.is_approved = False
    user.is_active = False
    user.save()
    
    send_mail(
        subject="Your Account Has Been Rejected",
        message=f"Dear {user.get_full_name()}, we regret to inform you that your account as a {user.role.title()} was rejected.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    messages.warning(request, f"{user.get_full_name()} ({user.role}) rejected.")
    return redirect('principal_dashboard')

def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Role', 'Approved'])

    for user in CustomUser.objects.all():
        writer.writerow([user.get_full_name, user.email, user.role, user.is_approved])

    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_users_pdf(request):
    users = User.objects.all().order_by('role')
    context = {'users': users}
    return render_to_pdf('principal/user_list_pdf.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_student_fees_pdf(request):
    # Fetch student fee records
    fees = StudentFee.objects.select_related('student').order_by('-date')
    context = {'fees': fees}

    # Render template to HTML string
    template = get_template('principal/student_fees_pdf.html')
    html_string = template.render(context)
    html = HTML(string=html_string, base_url=settings.STATIC_ROOT)

    # Convert HTML to PDF using WeasyPrint
    pdf_file = BytesIO()
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(pdf_file)

    # Return PDF as a downloadable response
    pdf_file.seek(0)
    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="student_fees_report.pdf"'
    return response


@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_teacher_salaries_pdf(request):
    salaries = TeacherSalary.objects.select_related('teacher').order_by('-paid_date')
    context = {'salaries': salaries}
    return render_to_pdf('principal/teacher_salaries_pdf.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def filtered_student_fees(request):
    fees = StudentFee.objects.select_related('student')

    month = request.GET.get('month')
    year = request.GET.get('year')

    if month:
        fees = fees.annotate(month=ExtractMonth('date')).filter(month=month)
    if year:
        fees = fees.annotate(year=ExtractYear('date')).filter(year=year)

    context = {
        'fees': fees,
        'month_selected': month,
        'year_selected': year,
    }
    return render(request, 'principal/student_fees_filter.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def filtered_teacher_salaries(request):
    salaries = TeacherSalary.objects.select_related('teacher')

    month = request.GET.get('month')
    year = request.GET.get('year')

    if month:
        try:
            month = int(month)
            salaries = salaries.annotate(paid_month=ExtractMonth('paid_date')).filter(paid_month=month)
        except ValueError:
            pass  # handle invalid month value gracefully

    if year:
        try:
            year = int(year)
            salaries = salaries.annotate(paid_year=ExtractYear('paid_date')).filter(paid_year=year)
        except ValueError:
            pass  # handle invalid year value gracefully

    context = {
        'salaries': salaries,
        'month_selected': month,
        'year_selected': year,
    }
    return render(request, 'principal/teacher_salaries_filter.html', context)