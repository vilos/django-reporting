from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import reporting

@login_required(login_url="/")
def report_list(request):
    all_reports = reporting.all_reports()
    reports = []
    for slug, report in all_reports:
        reports.append((slug, report(request),))
    return render_to_response('reporting/list.html', {'reports': reports}, context_instance=RequestContext(request))

@login_required(login_url="/")
def view_report(request, slug):
    report = reporting.get_report(slug)(request)
    data = {'report': report, 'title':report.verbose_name}
    return render_to_response(report.template_name, data, context_instance=RequestContext(request))
