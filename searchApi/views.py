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


def home(request):
    return render(request, 'index_login.html')


@csrf_exempt
def handleSignup(request):
    if request.method == 'POST':
        username = request.POST['signup_username']
        email = request.POST['signup_email']
        pass1 = request.POST['signup_pass1']
        pass2 = request.POST['signup_pass2']
        if pass1 != pass2:
            return redirect('/signup')

        try:
            new_user = User.objects.create_user(username, email, pass1)
        except:
            return redirect('/signup')
        new_user.save()
        print('User created')
        return redirect('/signup')
    else:
        return render(request, 'index_login.html')


@csrf_exempt
def handlelogin(request):
    if request.method == "POST":
        username = request.POST['signin_username']
        password = request.POST['signin_password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/stacksearch')
        else:
            return redirect('/signup')


@csrf_exempt
def handlelogout(request):
    print(request.user)
    logout(request)
    return redirect('/')


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

    if page != '':
        api_url += 'page='+page+'&'

    if pagesize != '':
        api_url += 'pagesize='+pagesize+'&'

    if fromdate != '':
        fromdate = getTimeStamp(fromdate)
        api_url += 'fromdate='+fromdate+'&'

    if todate != '':
        todate = getTimeStamp(todate)
        api_url += 'fromdate='+todate+'&'

    if order != 'Choose...':
        api_url += 'order='+order+'&'

    if min != '':
        min = getTimeStamp(min)
        api_url += 'order='+min+'&'

    if max != '':
        max = getTimeStamp(max)
        api_url += 'order='+max+'&'

    if sort != 'Choose...':
        api_url += 'sort='+sort+'&'

    if tag != '':
        api_url += 'tagged='+tag+'&'

    api_url += 'site=stackoverflow'

    valid, res = increase_search_count(user, query, api_url)
    if not valid:
        return HttpResponse('<h1>Limit Exceeded</h1>')
    html = get_search_html(res['items'])
    return HttpResponse(html)


def get_search_html(data):
    html = ""

    for i in data:
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


def increase_search_count(user, searched, apiurl):
    d = searchedData.objects.filter(
        user=user, date=str(date.today())).order_by('id')
    tz = pytz.timezone('Asia/Kolkata')

    for i in d:
        if searched.strip() == str(i.search).strip():
            return True, i.response

    if len(d) > 5:
        d = list(d)
        ins = d[-4]
        now = datetime.datetime.now(tz)
        usagetime = get_total_time(ins.time, now)

        if usagetime < 1:
            return False, ''

    elif len(d) > 100:
        return False, ''

    response = get_response(apiurl)

    ins = searchedData(user=user,
                       date=str(date.today()),
                       search=searched,
                       response=response,
                       time=str(datetime.datetime.now(tz)),
                       )
    ins.save()

    return True, response
