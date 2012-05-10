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
import httplib, json

def current_datetime(request):
    current_date = datetime.datetime.now()
    return render_to_response('current_datetime.html', {'current_date':current_date})

def hours_ahead(request, offset):
    offset = int(offset)
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    return render_to_response('hours_ahead.html', {'hour_offset': offset, 'next_time': dt})
    


def say_hello(request):
    lattitude = request.POST.get('lattitude', '41')
    longtitude = request.POST.get('longtitude', '74')
    range_ = request.POST.get('range', '50')
    
    conn = httplib.HTTPConnection('search.twitter.com')
    conn.request('GET', '/search.json?geocode=%s,%s,%smi&rpp=200&page=1' %(lattitude, longtitude, range_))
    result = conn.getresponse()
    resultstatus = result.status
    resultcontent = result
    data = json.load(resultcontent)
    result_list = data['results']
#    for l in result_list:
#        print l['from_user'],':', l['from_user_name'].encode('ascii'), l['profile_image_url'], l['text'].encode('utf8')
    conn.close()
    return render_to_response('localtweets.html', {'item_list': result_list})

def default (request):
#    lattitude = request.POST.get('lattitude', '')
#    longtitude = request.POST.get('longtitude', '')
#    range_ = request.POST.get('range', '') 
    return render_to_response('home.html', {})
