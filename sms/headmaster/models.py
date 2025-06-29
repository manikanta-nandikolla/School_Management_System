from django.db import models
from accounts.models import CustomUser
from django.conf import settings

# DO NOT import teachers.models directly here

class ClassSection(models.Model):
    CLASS_CHOICES = [
        ('1', '1st'), ('2', '2nd'), ('3', '3rd'), ('4', '4th'), ('5', '5th'),
        ('6', '6th'), ('7', '7th'), ('8', '8th'), ('9', '9th'), ('10', '10th'),
    ]
    class_name = models.CharField(max_length=10, choices=CLASS_CHOICES, unique=True)
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='class_teacher_for'
    )

    def __str__(self):
        return f"Class {self.class_name}"


class SubjectAssignment(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    subject = models.ForeignKey('teachers.Subject', on_delete=models.CASCADE)  # use string reference
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'subject', 'class_section')

    def __str__(self):
        return f"{self.teacher.get_full_name()} → {self.subject.name} ({self.class_section.class_name})"


class ClassTeacherAssignment(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    class_section = models.OneToOneField(ClassSection, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.class_section.class_name} - {self.teacher.get_full_name()}"


class ExamSchedule(models.Model):
    exam = models.ForeignKey('teachers.Exam', on_delete=models.CASCADE)  # use string reference
    subject = models.ForeignKey('teachers.Subject', on_delete=models.CASCADE)
    exam_date = models.DateField()
    exam_time = models.TimeField()
    class_section = models.ForeignKey(ClassSection, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.subject} ({self.exam}) – {self.exam_date}"
