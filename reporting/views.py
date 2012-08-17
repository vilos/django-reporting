import reporting

from django.contrib.auth.decorators import permission_required
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


class ReportListView(TemplateView):
    template_name = 'reporting/list.html'

    @method_decorator(permission_required("auth.can_view_reports"))
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

    @method_decorator(permission_required("auth.can_view_reports"))
    def dispatch(self, *args, **kwargs):
        return super(ReportView, self).dispatch(*args, **kwargs)

    def get(self, request, slug, **kwargs):
        self.slug = slug
        self.report = self.get_report(self.slug)
        return super(ReportView, self).get(request, **kwargs)

    def get_report(self, slug):
        try:
            return reporting.get_report(slug)(self.request)
        except reporting.ReportNotFound:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
        data = {'report': self.report, 'title': self.report.verbose_name,
                'media': self.report.admin.media}
        context.update(data)
        return context
