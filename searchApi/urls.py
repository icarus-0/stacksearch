from django.urls import path
from django.views.static import serve
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.handleSignup, name="handleSignup"),
    path('login', views.handlelogin, name="handlelogin"),
    path('logout', views.handlelogout, name="handlelogout"),
    path('stacksearch', views.stacksearch, name="stacksearch"),
    path('searchData', views.searchData, name="searchData")
]
