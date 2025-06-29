from django import forms
from .models import StudentFee, TeacherSalary
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()

CURRENT_YEAR = datetime.now().year
YEAR_CHOICES = [(year, str(year)) for year in range(CURRENT_YEAR, CURRENT_YEAR + 11)]

class StudentFeeForm(forms.ModelForm):
    class Meta:
        model = StudentFee
        fields = ['student', 'amount', 'status']
        
    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['student'].label_from_instance = lambda obj: f"{obj.roll_number} - {obj.get_full_name()}"


class TeacherSalaryForm(forms.ModelForm):
    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = TeacherSalary
        fields = ['teacher', 'basic', 'hra', 'bonus', 'deductions', 'amount', 'month', 'year', 'paid_date', 'note']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'basic': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'hra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'month': forms.Select(attrs={'class': 'form-control'}),
            'paid_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role__in=['teacher', 'headmaster', 'accountant'], is_approved=True)
        self.fields['note'].required = False
