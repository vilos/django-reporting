import reporting
from django.core.paginator import InvalidPage
from django.contrib.auth.decorators import permission_required
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, ListView


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


class ReportView(ListView):
    template_name = 'reporting/view.html'
    paginate_by = 100

    @method_decorator(permission_required("auth.can_view_reports"))
    def dispatch(self, *args, **kwargs):
        return super(ReportView, self).dispatch(*args, **kwargs)

    def get(self, request, slug, **kwargs):
        self.slug = slug
        self.report = self.get_report(self.slug)
        return super(ReportView, self).get(request, **kwargs)

    def get_queryset(self):
        return self.report.annotated_queryset

    def get_report(self, slug):
        try:
            return reporting.get_report(slug)(self.request)
        except reporting.ReportNotFound:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(ReportView, self).get_context_data(**kwargs)
        self.report.paginator = context['paginator']
        self.report.page_num = context['page_obj'].number - 1
        self.report.show_all = self.report.can_show_all = False
        self.report.multi_page = self.report.paginator.count > self.paginate_by
        data = {'report': self.report, 'title': self.report.verbose_name}
        context.update(data)
        return context

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, if needed.
        """
        paginator = self.get_paginator(
            queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        page = self.request.GET.get('p') or 0
        try:
            page_number = int(page) + 1
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_(u"Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage:
            raise Http404(_(u'Invalid page (%(page_number)s)') % {
                                'page_number': page_number
            })
