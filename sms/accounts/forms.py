from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from headmaster.models import ClassSection
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentRegisterForm(UserCreationForm):
    roll_number = forms.CharField(max_length=20, required=True, label="Roll Number")
    class_section = forms.ModelChoiceField(queryset=ClassSection.objects.all(), required=True, label="Class Section")

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'roll_number', 'class_section', 'password1', 'password2']

    def clean_roll_number(self):
        roll_number = self.cleaned_data['roll_number']
        if CustomUser.objects.filter(roll_number=roll_number).exists():
            raise ValidationError("A user with this roll number already exists.")
        return roll_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        user.username = self.cleaned_data['roll_number']  # assuming username is set to roll_number
        user.roll_number = self.cleaned_data['roll_number']
        user.class_section = self.cleaned_data['class_section']
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_section'].queryset = ClassSection.objects.all()

class StudentLoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput)
    
    
class TeacherRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'teacher'
        if commit:
            user.save()
        return user

class HeadmasterRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'headmaster'
        if commit:
            user.save()
        return user

class AccountantRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(AccountantRegisterForm, self).__init__(*args, **kwargs)

        # Add placeholders
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter your first name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter your last name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email address'})
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password'})
        
        for field in self.fields.values():
            field.help_text = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'accountant'
        user.is_approved = False
        user.is_rejected = False
        if commit:
            user.save()
        return user
    
# Forgot Password
class RolePasswordResetForm(PasswordResetForm):

    def __init__(self, *args, role=None, **kwargs):
        self.role = role
        super().__init__(*args, **kwargs)

    def get_users(self, email):
        qs = User.objects.filter(is_active=True, email__iexact=email)
        if self.role:
            qs = qs.filter(role=self.role) | qs.filter(is_superuser=True)
        for user in qs.distinct():
            if user.has_usable_password():
                yield user