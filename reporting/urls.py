from django.conf.urls.defaults import patterns, url
from .views import ReportListView, ReportView

urlpatterns = patterns('',
    url('^$', ReportListView.as_view(), name='reporting-list'),
    url('^(?P<slug>.*)/$', ReportView.as_view(), name='reporting-view'),
)
