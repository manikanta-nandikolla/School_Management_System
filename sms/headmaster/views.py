from django.shortcuts import render, redirect
from accounts.models import CustomUser
from accountant.models import TeacherSalary
from .models import ClassTeacherAssignment, SubjectAssignment, ClassSection, ExamSchedule
from django.http import JsonResponse, FileResponse
from .forms import TeacherForm, StudentForm, SubjectAssignmentForm,ClassTeacherAssignmentForm, ExamScheduleForm
from accountant.forms import TeacherSalaryForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
# Create your views here.
@login_required
def headmaster_dashboard(request):
    if request.user.role != 'headmaster':
        return redirect('headmaster_login')

    students = CustomUser.objects.filter(role='student')
    teachers = CustomUser.objects.filter(role='teacher')
    pending_users = CustomUser.objects.filter(role__in=['teacher', 'student'], is_approved=False)
    messages.info(request, "Welcome to your dashboard.")
    return render(request, 'headmaster/dashboard.html', {
        'students': students,
        'teachers': teachers,
        'pending_users' : pending_users,
    })

@login_required
def view_teacher_profile(request, pk):
    teacher = CustomUser.objects.get(id=pk, role='teacher')
    class_assignment = ClassTeacherAssignment.objects.filter(teacher=teacher).first()
    subject_assignments = SubjectAssignment.objects.filter(teacher=teacher)
    try:
        teacher = CustomUser.objects.get(id=pk, role='teacher')
    except CustomUser.DoesNotExist:
        messages.error(request, "Teacher not found.")
        return redirect('headmaster_dashboard')
    context = {
        'teacher': teacher,
        'class_assignment': class_assignment,
        'subject_assignments': subject_assignments,
    }

    return render(request, 'headmaster/view_teacher.html', context)

@login_required
def view_student_profile(request, pk):
    try:
        student = CustomUser.objects.get(id=pk, role='teacher')
    except CustomUser.DoesNotExist:
        messages.error(request, "Teacher not found.")
        return redirect('headmaster_dashboard')

    return render(request, 'headmaster/view_student.html', {'student': student})

@login_required
def manage_teacher_salary(request):
    if request.user.role != 'headmaster':
        return redirect('headmaster_login')

    if request.method == 'POST':
        form = TeacherSalaryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Salary entry saved successfully.")
            return redirect('manage_teacher_salary')
    else:
        messages.error(request, "Failed to save salary. Please check the form.")
        form = TeacherSalaryForm()

    salaries = TeacherSalary.objects.all().order_by('-year', '-month')
    return render(request, 'headmaster/manage_salary.html', {
        'form': form,
        'salaries': salaries
    })
    
@login_required
def edit_teacher_salary(request, salary_id):
    if request.user.role != 'headmaster':
        return redirect('headmaster_login')

    salary = get_object_or_404(TeacherSalary, id=salary_id)
    if request.method == 'POST':
        form = TeacherSalaryForm(request.POST, instance=salary)
        if form.is_valid():
            messages.error(request, "Failed to update salary. Please correct the errors.")
            form.save()
            messages.success(request, "Salary updated successfully.")
            return redirect('manage_teacher_salary')
    else:
        form = TeacherSalaryForm(instance=salary)
    
    return render(request, 'headmaster/edit_salary.html', {'form': form})

@login_required
def delete_teacher_salary(request, salary_id):
    if request.user.role != 'headmaster':
        return redirect('headmaster_login')

    salary = get_object_or_404(TeacherSalary, id=salary_id)
    salary.delete()
    messages.warning(request, "You are deleting a salary record. This action cannot be undone.")
    messages.success(request, "Salary record deleted.")
    return redirect('manage_teacher_salary')

@login_required
def delete_teacher(request, teacher_id):
    if request.user.role != 'headmaster':
        return redirect('headmaster_login')

    if request.method == 'POST':
        teacher = get_object_or_404(CustomUser, id=teacher_id, role='teacher')
        teacher_name = teacher.get_full_name()
        teacher.delete()
        messages.success(request, f"Teacher {teacher_name} deleted successfully.")
    return redirect('headmaster_dashboard')


@login_required
def delete_student(request, student_id):
    if request.user.role != 'headmaster':
        return redirect('headmaster_login')

    if request.method == 'POST':
        student = get_object_or_404(CustomUser, id=student_id, role='student')
        student_name = student.get_full_name()
        student.delete()
        messages.success(request, f"Student {student_name} deleted successfully.")
    return redirect('headmaster_dashboard')

@login_required
def headmaster_salary_view(request):
    if request.user.role != 'headmaster':
        return redirect('login')

    salaries = TeacherSalary.objects.filter(teacher=request.user).order_by('-year', '-month')
    return render(request, 'headmaster/salary_view.html', {'salaries': salaries})

@login_required
def assign_class_teacher(request):
    if request.method == 'POST':
        form = ClassTeacherAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class teacher assigned successfully.')
            return redirect('assign_class_teacher')
    else:
        form = ClassTeacherAssignmentForm()

    assignments = ClassTeacherAssignment.objects.all()
    class_sections = ClassSection.objects.all()

    # Filtering logic
    teacher_query = request.GET.get('teacher')
    class_filter = request.GET.get('class')

    if teacher_query:
        assignments = assignments.filter(teacher__full_name__icontains=teacher_query)

    if class_filter:
        assignments = assignments.filter(class_section__id=class_filter)

    return render(request, 'headmaster/assign_class_teacher.html', {
        'form': form,
        'assignments': assignments,
        'class_sections': class_sections,
    })


@login_required
def assign_subject_teacher(request):
    if request.method == 'POST':
        form = SubjectAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('assign_subject_teacher')
    else:
        form = SubjectAssignmentForm()

    assignments = SubjectAssignment.objects.all()
    return render(request, 'headmaster/assign_subject_teacher.html', {'form': form, 'assignments': assignments})

# ---- CLASS TEACHER ----

@login_required
def edit_class_teacher(request, pk):
    assignment = get_object_or_404(ClassTeacherAssignment, pk=pk)
    if request.method == 'POST':
        form = ClassTeacherAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Class teacher updated successfully.")
            return redirect('assign_class_teacher')
    else:
        form = ClassTeacherAssignmentForm(instance=assignment)

    return render(request, 'headmaster/edit_class_teacher.html', {'form': form})


@login_required
def delete_class_teacher(request, pk):
    assignment = get_object_or_404(ClassTeacherAssignment, pk=pk)
    assignment.delete()
    messages.success(request, "Class teacher assignment deleted.")
    return redirect('assign_class_teacher')


# ---- SUBJECT TEACHER ----

@login_required
def edit_subject_teacher(request, pk):
    assignment = get_object_or_404(SubjectAssignment, pk=pk)
    if request.method == 'POST':
        form = SubjectAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Subject teacher updated successfully.")
            return redirect('assign_subject_teacher')
    else:
        form = SubjectAssignmentForm(instance=assignment)

    return render(request, 'headmaster/edit_subject_teacher.html', {'form': form})


@login_required
def delete_subject_teacher(request, pk):
    assignment = get_object_or_404(SubjectAssignment, pk=pk)
    assignment.delete()
    messages.success(request, "Subject teacher assignment deleted.")
    return redirect('assign_subject_teacher')

@login_required
def view_my_payslip(request, pk):
    salary = get_object_or_404(TeacherSalary, pk=pk, teacher=request.user)
    if not salary.payslip:
        messages.warning(request, "Payslip not available.")
        return redirect('my_payslips') 
    return FileResponse(salary.payslip.open(), content_type='application/pdf')


@login_required
def download_my_payslip(request, pk):
    salary = get_object_or_404(TeacherSalary, pk=pk, teacher=request.user)
    if not salary.payslip:
        messages.warning(request, "Payslip not available.")
        return redirect('my_payslips') 
    response = FileResponse(salary.payslip.open(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payslip_{salary.pk}.pdf"'
    return response

@login_required
def schedules_list(request):
    schedules = ExamSchedule.objects.all()
    return render(request, "headmaster/schedules_list.html", {"schedules": schedules})

@login_required
def schedule_create(request):
    session_key = 'temp_exam_schedules'

    # Initialize session storage if not present
    if session_key not in request.session:
        request.session[session_key] = []

    if request.method == "POST":
        form = ExamScheduleForm(request.POST or None, headmaster=request.user)
        action = request.POST.get("action")

        if form.is_valid():
            data = form.cleaned_data

            # Prepare serialized schedule for session
            schedule_data = {
                "exam": str(data["exam"]),
                "subject": str(data["subject"]),
                "exam_date": str(data["exam_date"]),
                "exam_time": str(data["exam_time"]),
                "class_section": str(data["class_section"]),
                "exam_id": data["exam"].id,
                "subject_id": data["subject"].id,
                "class_section_id": data["class_section"].id,
            }

            if action == "add_another":
                request.session[session_key].append(schedule_data)
                request.session.modified = True
                messages.success(request, "Schedule added temporarily.")
                form = ExamScheduleForm(headmaster=request.user)
            elif action == "save":

                temp_data = request.session[session_key] + [schedule_data]
                for item in temp_data:
                    ExamSchedule.objects.create(
                        exam_id=item["exam_id"],
                        subject_id=item["subject_id"],
                        exam_date=item["exam_date"],
                        exam_time=item["exam_time"],
                        class_section_id=item["class_section_id"],
                        created_by=request.user
                    )
                del request.session[session_key]
                messages.success(request, "All schedules saved.")
                return redirect("headmaster_exam_schedules")
    else:
        form = ExamScheduleForm(headmaster=request.user)

    return render(
        request,
        "headmaster/schedule_form.html",
        {
            "form": form,
            "edit_mode": False,
            "temp_schedules": request.session.get(session_key, [])
        },
    )
    
@login_required
def schedule_update(request, pk):
    sched = get_object_or_404(ExamSchedule, pk=pk, created_by=request.user)

    if request.method == "POST":
        form = ExamScheduleForm(request.POST, instance=sched, headmaster=request.user)
        if form.is_valid():
            form.save()
            return redirect("headmaster_exam_schedules")
    else:
        form = ExamScheduleForm(instance=sched, headmaster=request.user)

    return render(request, "headmaster/schedule_form.html", {"form": form, "edit_mode": True},)

@login_required
def schedule_delete(request, pk):
    sched = get_object_or_404(ExamSchedule, pk=pk, created_by=request.user)

    if request.method == "POST":
        sched.delete()
        return redirect("headmaster_exam_schedules")

    return render(request, "headmaster/schedule_confirm_delete.html", {"schedule": sched},)