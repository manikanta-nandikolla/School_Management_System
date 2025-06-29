from django.db import models
from accounts.models import CustomUser
from django.utils import timezone
# Create your models here.
class Notice(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    posted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    event_date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} on {self.date}"

class Holiday(models.Model):
    name = models.CharField(max_length=100)
    holiday_date = models.DateField()
    description = models.TextField(null=True)
    
    def __str__(self):
        return f"{self.name} ({self.date})"