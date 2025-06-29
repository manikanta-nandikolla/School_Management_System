from django import forms
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from .models import Attendance, Mark, Exam, Subject
from datetime import date
from headmaster.models import SubjectAssignment, ClassSection, ClassTeacherAssignment

class StudentForm(forms.ModelForm):
    class_section = forms.ModelChoiceField(
        queryset=ClassSection.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Class Section"
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'roll_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

class AttendanceForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today,
        label="Attendance Date"
    )

    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status']

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['student'].widget.attrs.update({'class': 'form-control'})
        self.fields['date'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})

        if teacher:
            class_assignments = ClassTeacherAssignment.objects.filter(teacher=teacher)
            if class_assignments.exists():
                section_ids = class_assignments.values_list('class_section', flat=True)
                self.fields['student'].queryset = CustomUser.objects.filter(role='student', class_section__in=section_ids)
            else:
                self.fields['student'].queryset = CustomUser.objects.none()
        else:
            self.fields['student'].queryset = CustomUser.objects.none()

        self.fields['student'].label_from_instance = lambda obj: f"{obj.roll_number} - {obj.get_full_name()}"

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        attendance_date = cleaned_data.get('date')

        if student and attendance_date:
            exists = Attendance.objects.filter(student=student, date=attendance_date).exists()
            if exists:
                raise ValidationError(f"Attendance for {student.get_full_name()} on {attendance_date} has already been recorded.")
         
class MarkForm(forms.ModelForm):
    custom_subject = forms.CharField(required=False, label="Custom Subject", widget=forms.TextInput(attrs={'style': 'display:none;'}))

    class Meta:
        model = Mark
        fields = ['student', 'subject', 'custom_subject', 'marks_obtained', 'exam']

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)

        if teacher:
            class_assignments = ClassTeacherAssignment.objects.filter(teacher=teacher)
            if class_assignments.exists():
                section_ids = class_assignments.values_list('class_section', flat=True)
                self.fields['student'].queryset = CustomUser.objects.filter(role='student', class_section__in=section_ids)
            else:
                self.fields['student'].queryset = CustomUser.objects.none()
        else:
            self.fields['student'].queryset = CustomUser.objects.none()

        self.fields['student'].label_from_instance = lambda obj: f"{obj.roll_number} - {obj.get_full_name()}"
