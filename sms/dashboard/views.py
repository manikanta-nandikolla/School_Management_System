from django.shortcuts import render
from principal.models import Notice, Event, Holiday
# Create your views here.
def index_page(request):
    notices = Notice.objects.order_by('-date_posted')[:5]
    events = Event.objects.order_by('event_date')[:5]
    holidays = Holiday.objects.order_by('holiday_date')[:5]
    return render(request, 'index.html', {
        'notices': notices,
        'events': events,
        'holidays': holidays,
    })