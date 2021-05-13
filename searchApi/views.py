from re import search
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import requests
import json
import time
import datetime
from datetime import date
import pytz
# Create your views here.

search_timestamp = [0]*5

try:
    with open('./data/cached.json') as json_file:
        cached_data = json.load(json_file)
except:
    cached_data = {}


def home(request):
    return render(request, 'stackSearch.html')


def stacksearch(request):
    return render(request, 'stackSearch.html')


def getTimeStamp(date):
    y, m, d = date.split('-')
    date = d+'/'+m+'/'+y
    a = time.mktime(datetime.datetime.strptime(date, "%d/%m/%Y").timetuple())
    return str(int(a))


@csrf_exempt
def searchData(request):
    user = request.user
    page = request.POST['page']
    pagesize = request.POST['pagesize']
    fromdate = request.POST['fromdate']
    todate = request.POST['todate']
    min = request.POST['min']
    max = request.POST['max']
    order = request.POST['order']
    sort = request.POST['sort']
    tag = request.POST['tag']
    query = request.POST['query']

    api_url = 'https://api.stackexchange.com/2.2/questions?'
    cacheid = ''
    if page != '':
        api_url += 'page='+page+'&'
        cacheid += page

    if pagesize != '':
        api_url += 'pagesize='+pagesize+'&'
        cacheid += pagesize

    if fromdate != '':
        fromdate = getTimeStamp(fromdate)
        api_url += 'fromdate='+fromdate+'&'
        cacheid += fromdate

    if todate != '':
        todate = getTimeStamp(todate)
        api_url += 'fromdate='+todate+'&'
        cacheid += todate

    if order != 'Choose...':
        api_url += 'order='+order+'&'
        cacheid += order

    if min != '':
        min = getTimeStamp(min)
        api_url += 'order='+min+'&'
        cacheid += min

    if max != '':
        max = getTimeStamp(max)
        api_url += 'order='+max+'&'
        cacheid += max

    if sort != 'Choose...':
        api_url += 'sort='+sort+'&'
        cacheid += sort

    if tag != '':
        api_url += 'tagged='+tag+'&'
        cacheid += tag

    api_url += 'site=stackoverflow'
    cacheid += query

    valid, res = increase_search_count(query, api_url, cacheid)
    if not valid:
        return HttpResponse('<h1>Limit Exceeded</h1>')
    html = get_search_html(res['items'], query)
    return HttpResponse(html)


def get_search_html(data, query):
    html = ""
    checker = False
    for i in data:
        if query in i['title'] or i['title'] in query:
            checker = True
            html += ''' <div class="card w-50 mx-auto mt-3">
                    <div class="card-header">
                    <a href="">
                        <img
                        src =" '''+i['owner']['profile_image'] + '''"
                        alt="https://visualpharm.com/assets/30/User-595b40b85ba036ed117da56f.svg"
                        style="width: 50px; height: 50px"
                        />
                        <h6>'''+i['owner']['display_name'] + '''</h6>
                    </a>
                    </div>
                    <div class="card-body">
                    <blockquote class="blockquote mb-0">
                    <a href="'''+i['link'] + '''">
                        <p>'''+i['title']+'''</p>
                    </a>
                        <footer class="blockquote-footer"> Tags ''' + str(i['tags']) + '''</footer>
                    </blockquote>
                    </div>
                </div>'''

    if not checker:
        return '''<h1>Sorry We Didn't find any matching Question title with your query ..!</h1>'''
    return html


def get_response(api_url):
    response = requests.get(api_url)
    return response.json()


def get_total_time(p, p1):
    p = str(p).split('+')[0]
    p1 = str(p1).split('+')[0]
    p = datetime.datetime. strptime(p, '%Y-%m-%d %H:%M:%S.%f')
    p1 = datetime.datetime. strptime(p1, '%Y-%m-%d %H:%M:%S.%f')
    c = (p1 - p)
    minute = c.total_seconds()/60

    return minute


def increase_search_count(searched, apiurl, cacheid):
    d = cached_data
    tz = pytz.timezone('Asia/Kolkata')

    for i in cached_data:
        if cacheid.strip() == i.strip():
            return True, cached_data[i][0]

    if len(d.keys()) > 5:
        d = list(d.keys())
        ins = d[-4]
        now = datetime.datetime.now(tz)

        usagetime = get_total_time(cached_data[ins][1], now)

        if usagetime < 1:
            return False, ''

    elif len(d.keys()) > 100:
        return False, ''

    response = get_response(apiurl)

    cached_data[cacheid] = [response, str(datetime.datetime.now(tz))]
    with open("./data/cached.json", "w") as fp:
        json.dump(cached_data, fp)

    return True, response
