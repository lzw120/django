#from django.template.loader import get_template
#from django.http import HttpResponse
#from django.template import Context
#import datetime
#
#def current_datetime(request):
#    now = datetime.datetime.now()
#    html = "<html><body>It is now %s.</body></html>" %now
#    return HttpResponse(html)
#
#def hours_ahead(request, offset):
#    offset = int (offset)
#    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
#    html = "<html><body>In %s hour(s), it will be %s.</body></html>" %(offset, dt)
#    return HttpResponse(html)
#
#def say_hello(request):
#    person = {'last_name': 'Li', 'first_name':'Zewen'}
#    t = get_template('try.html')
#    c = Context({'person': person})
#    print t.render(c)
#    return HttpResponse(t.render(c))
#


# let's use render_to_response()
# that's much simpler than our say_hello
from django.shortcuts import render_to_response
import datetime


def current_datetime(request):
    current_date = datetime.datetime.now()
    return render_to_response('current_datetime.html', {'current_date':current_date})

def hours_ahead(request, offset):
    offset = int(offset)
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    return render_to_response('hours_ahead.html', {'hour_offset': offset, 'next_time': dt})
    


def say_hello(request):
    person = {'last_name': 'Li', 'first_name':'Zewen'}
    return render_to_response('try.html', {'person': person})
