from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import logout, get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
from .forms import *
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import EmailMultiAlternatives
from django.http import Http404
User = get_user_model()
ALLOWED_ROLES = {"student", "teacher", "headmaster", "principal", "accountant"}
# Create your views here.
# Logout
def logout_view(request):
    logout(request)
    return render(request, 'accounts/logout.html')

# Student registration    
def student_register_view(request):
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful! wait for the Principal approval")
            login(request, user)
            return redirect('index')
    else:
        form = StudentRegisterForm()
    return render(request, 'accounts/student_register.html', {'form': form})

# Student login
def student_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user and user.role == 'student':
            if user.is_approved:
                login(request, user)
                return redirect('student_dashboard')
            else:
                messages.warning(request, "Your account is pending approval by the Principal.")
        else:
            messages.error(request, "Invalid login credentials.")
    return render(request, 'accounts/student_login.html')


# Teacher login
def teacher_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user and user.role == 'teacher':
            if user.is_approved:
                login(request, user)
                return redirect('teacher_dashboard')
            else:
                messages.warning(request, "Your account is pending approval by the Principal.")
        else:
            messages.error(request, "Invalid login credentials.")
    return render(request, 'accounts/teacher_login.html')

# Teacher registration
def teacher_register_view(request):
    if request.method == 'POST':
        form = TeacherRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! wait for the Principal approval")
            return redirect('index')
    else:
        form = TeacherRegisterForm()
    return render(request, 'accounts/teacher_register.html', {'form': form})

# Headmaster registration
def headmaster_register_view(request):
    if request.method == 'POST':
        form = HeadmasterRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! wait for the Principal approval")
            return redirect('index')
    else:
        form = HeadmasterRegisterForm()
    return render(request, 'accounts/headmaster_register.html', {'form': form})

# Headmaster login
def headmaster_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None and user.role == 'headmaster':
            if user.is_approved:
                login(request, user)
                return redirect('headmaster_dashboard')
        else:
            messages.error(request, "Invalid credentials or unauthorized user.")
    return render(request, 'accounts/headmaster_login.html')

# Principal login
def principal_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user and user.is_superuser:
            login(request, user)
            return redirect('principal_dashboard')
        else:
            messages.error(request, "Invalid credentials or not a principal account.")
    
    return render(request, 'accounts/principal_login.html')

# Accountant registration
def accountant_register(request):
    if request.method == 'POST':
        form = AccountantRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Accountant registration submitted. Awaiting principal approval.')
            return redirect('index')
    else:
        form = AccountantRegisterForm()
    return render(request, 'accounts/accountant_register.html', {'form': form})

# Accountant login
def accountant_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == 'accountant':
            if user.is_approved:
                login(request, user)
                return redirect('accountant_dashboard')
            else:
                messages.warning(request, 'Awaiting principal approval.')
        else:
            messages.error(request, 'Invalid login.')
    return render(request, 'accounts/accountant_login.html')

# Forgot Password
def password_reset_request(request, role):
    role = role.lower()
    if role not in ALLOWED_ROLES:
        raise Http404("Role not found")

    if request.method == "POST":
        form = RolePasswordResetForm(request.POST, role=role)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                email_template_name="accounts/password_reset_email.html",
                subject_template_name="accounts/password_reset_subject.txt",
                token_generator=default_token_generator,
            )
            return redirect("password_reset_done")
    else:
        form = RolePasswordResetForm(role=role)

    return render(request, "accounts/password_reset.html", {"form": form, "role": role})


def password_reset_done(request):
    return render(request, "accounts/password_reset_done.html")


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (ValueError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, "accounts/password_reset_invalid.html")

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password updated. Please log in.")
            return redirect("password_reset_complete")
    else:
        form = SetPasswordForm(user)

    return render(request, "accounts/password_reset_confirm.html", {"form": form})


def password_reset_complete(request):
    return render(request, "accounts/password_reset_complete.html")

def forgot_password_role_selector(request):
    return render(request, "accounts/forgot_password_role_selector.html")
