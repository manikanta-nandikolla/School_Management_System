from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, FileResponse, HttpResponse
from accounts.models import CustomUser
from accountant.models import TeacherSalary
from .models import Attendance, Mark, LeaveRequest, Subject, Exam, StudentClassAssignment
from accountant.models import TeacherSalary
from headmaster.models import SubjectAssignment, ClassSection, ClassTeacherAssignment, ExamSchedule
from .forms import StudentForm, AttendanceForm, MarkForm
from headmaster.forms import ExamScheduleForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from django.core.mail import send_mail
from django.utils.html import format_html, strip_tags
from django.conf import settings
# Create your views here.
def is_teacher(user):
    return user.is_authenticated and user.role == 'teacher'

@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('teacher_login')

    assignments = ClassTeacherAssignment.objects.filter(teacher=request.user)
    if not assignments.exists():
        students = CustomUser.objects.none()
        messages.error(request, "You are not assigned to any class.")
    else:
        section_ids = assignments.values_list('class_section', flat=True)
        students = CustomUser.objects.filter(role='student', class_section__in=section_ids)

    return render(request, 'teachers/dashboard.html', {'students': students})

@login_required
def record_attendance(request):
    if request.user.role != 'teacher':
        return redirect('login')

    form = AttendanceForm(request.POST or None, teacher=request.user)

    if form.is_valid():
        attendance = form.save()

        # Send absent email if needed
        if attendance.status.strip().lower() == 'absent':
            subject = f"🚫 Absence Notification - {attendance.date}"
            html_message = format_html("""
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #e74c3c;">Absence Notification</h2>
                    <p>Dear <strong>{name}</strong>,</p>
                    <p>
                        Our records show that you were marked <strong style="color:#e74c3c;">Absent</strong> 
                        on <strong>{date}</strong> by your class teacher.
                    </p>
                    <p>If this is incorrect, please speak with your class teacher immediately.</p>
                    <p style="margin-top: 20px;">Regards,<br><em>Sree Vidyalaya EM High School</em></p>
                    <hr>
                    <small>This is an automated email. Please do not reply.</small>
                </div>
            """, name=attendance.student.get_full_name(), date=attendance.date)

            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[attendance.student.email],
                html_message=html_message,
            )

        messages.success(request, "Attendance recorded successfully.")
        return redirect('teacher_dashboard')

    return render(request, 'teachers/record_attendance.html', {'form': form})

# Add marks
@login_required
def add_marks(request):
    if request.user.role != 'teacher':
        return redirect('login')

    assignments = ClassTeacherAssignment.objects.filter(teacher=request.user)
    if not assignments.exists():
        messages.error(request, "You are not assigned to any class.")
        return redirect('teacher_dashboard')

    section_ids = list(assignments.values_list('class_section', flat=True))
    form = MarkForm(request.POST or None, teacher=request.user)

    student_id = request.GET.get('student')
    exam_id = request.GET.get('exam')
    student = None
    exam = None
    submitted_marks = []

    if student_id and exam_id:
        try:
            student = CustomUser.objects.get(id=student_id, role='student', class_section__in=section_ids)
            exam = Exam.objects.get(id=exam_id)
            session_key = f"submitted_marks_{student.id}_{exam.id}"
            submitted_marks = request.session.get(session_key, [])
        except (CustomUser.DoesNotExist, Exam.DoesNotExist):
            messages.error(request, "Invalid student or exam.")
            return redirect('teacher_dashboard')

    if request.method == 'POST' and form.is_valid():
        mark = form.save(commit=False)

        if mark.student.class_section_id not in section_ids:
            messages.error(request, "You can only add marks for your class students.")
        else:
            mark.class_section = mark.student.class_section
            mark.save()

            session_key = f"submitted_marks_{mark.student.id}_{mark.exam.id}"
            submitted_marks = request.session.get(session_key, [])

            subject_name = mark.custom_subject if mark.subject.name == "Others" else mark.subject.name
            entry = f"{mark.student.get_full_name()}: {subject_name} - {mark.marks_obtained}"
            submitted_marks.append(entry)
            request.session[session_key] = submitted_marks

            if request.POST.get("save") == "another":
                messages.success(request, "Mark saved. Add another subject.")
                return redirect(f"{request.path}?student={mark.student.id}&exam={mark.exam.id}")
            else:
                if session_key in request.session:
                    del request.session[session_key]
                messages.success(request, "Mark saved successfully.")
                return redirect('teacher_dashboard')

    return render(request, 'teachers/add_marks.html', {
        'form': form,
        'last_marks': submitted_marks,
    })

@login_required
def leave_approval_view(request):
    if request.user.role != 'teacher':
        return redirect('login')

    assignments = ClassTeacherAssignment.objects.filter(teacher=request.user)
    if not assignments.exists():
        messages.error(request, "You are not assigned to any class.")
        return redirect('teacher_dashboard')

    section_ids = list(assignments.values_list('class_section', flat=True))
    leave_requests = LeaveRequest.objects.filter(student__class_section__in=section_ids, status='Pending')

    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')
        leave = get_object_or_404(LeaveRequest, id=leave_id)

        if leave.student.class_section_id not in section_ids:
            messages.error(request, "You can only manage leave requests for your class.")
        else:
            leave.status = 'Approved' if action == 'approve' else 'Rejected'
            leave.save()
            messages.success(request, f"Leave request {leave.status.lower()}.")

        return redirect('leave_approval')

    return render(request, 'teachers/leave_approval.html', {'leave_requests': leave_requests})

@login_required
def teacher_salary_view(request):
    if request.user.role != 'teacher':
        messages.error(request, "Access denied. You must be a teacher to view salaries.")
        return redirect('login')

    salaries = TeacherSalary.objects.filter(teacher=request.user).order_by('-year', '-month')
    return render(request, 'teachers/salary_view.html', {'salaries': salaries})

@login_required
@user_passes_test(is_teacher)
def view_salary_records(request):
    salaries = request.user.salaries.all()
    if not salaries.exists():
        messages.info(request, "No salary records available.")
    return render(request, 'teachers/salary_view.html', {'salaries': salaries})

@login_required
def my_salary_records(request):
    if request.user.role != 'teacher':
        messages.error(request, "Unauthorized access. Only teachers can view this page.")
        return redirect('teacher_login')

    salaries = TeacherSalary.objects.filter(teacher=request.user).order_by('-year', '-month')
    return render(request, 'teachers/my_salary.html', {'salaries': salaries})

@login_required
def my_payslips(request):
    if request.user.role != 'teacher':
        messages.error(request, "You are not authorized to view payslips.")
        return HttpResponse("Unauthorized", status=403)

    salaries = TeacherSalary.objects.filter(teacher=request.user).order_by('-year', '-month')
    return render(request, 'teachers/salary_view.html', {'salaries': salaries})

@login_required
def download_payslip(request, pk):
    payslip = get_object_or_404(TeacherSalary, pk=pk, teacher=request.user)

    if payslip.payslip:
        return FileResponse(payslip.payslip.open(), content_type='application/pdf')

    messages.warning(request, "Payslip not available.")
    return redirect('my_payslips')

@login_required
def schedules_list(request):
    schedules = ExamSchedule.objects.order_by("-exam_date", "exam_time")
    if not schedules.exists():
        messages.info(request, "No exam schedules found.")
    return render(request, "teachers/schedules_list.html", {"schedules": schedules})


@login_required
def schedule_create(request):
    if request.method == "POST":
        form = ExamScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam schedule created.")
            return redirect("teacher_exam_schedules")
    else:
        form = ExamScheduleForm()

    return render(request, "teachers/schedule_form.html", {"form": form})