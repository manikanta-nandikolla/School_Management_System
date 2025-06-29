from django import forms
from accounts.models import CustomUser
from .models import SubjectAssignment, ClassTeacherAssignment, ExamSchedule, ClassSection
class TeacherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'teacher'
        if commit:
            user.save()
        return user

class StudentForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'roll_number']

class ClassTeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = ClassTeacherAssignment
        fields = ['teacher', 'class_section']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = CustomUser.objects.filter(role='teacher')


class SubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = SubjectAssignment
        fields = ['subject', 'class_section', 'teacher']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = CustomUser.objects.filter(role='teacher')
        
class ExamScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.headmaster = kwargs.pop('headmaster', None)
        super().__init__(*args, **kwargs)

        if self.headmaster:
            self.fields["class_section"].queryset = ClassSection.objects.all()
            

    class Meta:
        model = ExamSchedule
        fields = ["exam", "subject", "exam_date", "exam_time", "class_section"]
        widgets = {
            "exam_date": forms.DateInput(attrs={"type": "date"}),
            "exam_time": forms.TimeInput(attrs={"type": "time"}),
        }