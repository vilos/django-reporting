from django.conf.urls import *
from django.contrib import admin
from django.http import HttpResponseRedirect
import reporting

admin.autodiscover()
reporting.autodiscover()


def index(request):
    return HttpResponseRedirect('/admin/')

urlpatterns = patterns('',
    (r'^$', index),
    (r'^admin/', include(admin.site.urls)),
    (r'^reporting/', include('reporting.urls')),
)
