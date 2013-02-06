from django.conf import settings
from django.utils.datastructures import SortedDict
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from base import Report, SimpleReport  # NOQA

_registry = SortedDict()


class ReportNotFound(Exception):
    pass


def register(slug, klass):
    _registry[slug] = klass


def get_report(slug):
    try:
        return _registry[slug]
    except KeyError:
        raise ReportNotFound("No such report '%s'" % slug)


def all_reports():
    return _registry.items()


def user_reports(request):
    for slug, klass in all_reports():
        if klass.has_view_permission(request):
            yield slug, klass


def autodiscover():
    REPORTING_SOURCE_FILE = getattr(settings, 'REPORTING_SOURCE_FILE',
                                    'reports')
    modules = []
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)

        try:
            module = import_module('%s.%s' % (app, REPORTING_SOURCE_FILE))
        except:
            if module_has_submodule(mod, REPORTING_SOURCE_FILE):
                raise
        else:
            modules.append(module)
    return modules

def admin_urls(admin_site=None):
    """
    URLs for views with the `admin_view` decorator of a custom or the
    default admin-site.
    """
    from django.conf.urls import patterns, url
    from reporting.views import ReportListView, ReportView, ReportExportView

    if not admin_site:
        from django.contrib.admin import site as admin_site

    urlpatterns = patterns('',
        url('^$', admin_site.admin_view(ReportListView.as_view()),
            name='reporting-list'),
        url('^(?P<slug>[\w-]+)/$', admin_site.admin_view(ReportView.as_view()),
            name='reporting-view'),
        url('^(?P<slug>[\w-]+)/export/(?P<format>[\w-]+)/$',
            admin_site.admin_view(ReportExportView.as_view()),
            name='reporting-export'),
    )

    return urlpatterns
