from django.db import models
from accounts.models import CustomUser
from django.apps import apps  
from headmaster.models import ClassSection
from django.conf import settings

class Attendance(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    class Meta:
        unique_together = ('student', 'date')
        
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.status}"


class Exam(models.Model):
    EXAM_CHOICES = [
        ('FA-I', 'Formative Assessment I'),
        ('FA-II', 'Formative Assessment II'),
        ('FA-III', 'Formative Assessment III'),
        ('FA-IV', 'Formative Assessment IV'),
        ('SA-I', 'Summative Assessment I'),
        ('SA-II', 'Summative Assessment II'),
        ('SA-III', 'Summative Assessment III'),
    ]
    name = models.CharField(max_length=10, choices=EXAM_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Mark(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    custom_subject = models.CharField(max_length=100, blank=True, null=True)
    marks_obtained = models.FloatField(null=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, default=1)
    class_section = models.ForeignKey('headmaster.ClassSection', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        subject_display = self.subject.name if self.subject else self.custom_subject
        return f"{self.student.get_full_name()} - {subject_display} - {self.exam} - {self.marks_obtained}"

    def get_subject_display_name(self):
        return self.custom_subject if self.subject.name == 'Others' else self.subject.name


class LeaveRequest(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    reason = models.TextField()
    date_requested = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.status}"


# Extend CustomUser with class_section (using string reference)
CustomUser.add_to_class(
    'class_section',
    models.ForeignKey('headmaster.ClassSection', on_delete=models.SET_NULL, null=True, blank=True)
)


# Auto promotion utility function
def promote_students():
    class_order = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    ClassSection = apps.get_model('headmaster', 'ClassSection')

    for student in CustomUser.objects.filter(role='student'):
        current_class = student.class_section.name if student.class_section else None
        if current_class and current_class in class_order:
            current_index = class_order.index(current_class)
            if current_index < len(class_order) - 1:
                next_class = class_order[current_index + 1]
                next_section = ClassSection.objects.get(name=next_class)
                student.class_section = next_section
                student.save()

class StudentClassAssignment(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='class_assignment'
    )
    class_section = models.ForeignKey(
        ClassSection,
        on_delete=models.CASCADE,
        related_name='assigned_students'
    )

    def __str__(self):
        return f"{self.student.get_full_name()} → Class {self.class_section.class_name}"