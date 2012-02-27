from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import reporting


class ReportListView(TemplateView):
    template_name = 'reporting/list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReportListView, self).dispatch(*args, **kwargs)

    def get_reports(self):
        all_reports = reporting.all_reports()
        reports = []
        for slug, klass in all_reports:
            reports.append((slug, klass(self.request),))
        return reports

    def get_context_data(self, **kwargs):
        context = super(ReportListView, self).get_context_data(**kwargs)
        data = {'reports': self.get_reports()}
        context.update(data)
        return context


class ReportView(TemplateView):
    template_name = 'reporting/view.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReportView, self).dispatch(*args, **kwargs)

    def get_context_data(self, slug, **kwargs):
        context = super(ReportView, self).get_context_data(slug=slug, **kwargs)
        report = reporting.get_report(slug)(self.request)
        data = {'report': report, 'title': report.verbose_name}
        context.update(data)
        return context

