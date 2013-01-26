from django.conf.urls import patterns, url, include
from reporting import admin_urls

urlpatterns = patterns('',
    url('', include(admin_urls())),
)
