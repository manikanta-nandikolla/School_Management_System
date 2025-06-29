from django.contrib import admin
from teachers.models import Attendance,  Subject, Mark, LeaveRequest, Exam
from headmaster.models import ClassSection, SubjectAssignment,ExamSchedule, ClassTeacherAssignment
from .models import Event, Holiday, Notice
# Register your models here.

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_posted')
    search_fields = ('title',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_date', 'time')
    search_fields = ('name',)


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'holiday_date')
    search_fields = ('name',)
    

@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'class_teacher')
    search_fields = ('name',)
    list_filter = ('class_teacher',)


@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'class_section')
    list_filter = ('subject', 'class_section')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'subject__name')


@admin.register(ClassTeacherAssignment)
class ClassTeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('class_section', 'teacher')
    search_fields = ('teacher__first_name', 'teacher__last_name')


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('exam', 'subject', 'class_section', 'exam_date', 'exam_time', 'created_by')
    list_filter = ('exam', 'subject', 'exam_date')
    search_fields = ('exam__name', 'subject__name')
     
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('student__first_name', 'student__last_name')


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'custom_subject', 'marks_obtained', 'exam', 'class_section')
    list_filter = ('exam', 'subject', 'class_section')
    search_fields = ('student__first_name', 'student__last_name', 'subject__name')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'reason', 'date_requested', 'status')
    list_filter = ('status',)
    search_fields = ('student__first_name', 'student__last_name', 'reason')