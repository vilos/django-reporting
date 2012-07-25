# -*- coding: utf-8 -*-

from django import template
from django.contrib.admin.templatetags.admin_list import result_headers,\
        ResultList
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


def items_for_result(report, result):
    row_class = ''

    for field_name in report.list_display:
        result_repr = conditional_escape(result[field_name])
        yield mark_safe(u'<td%s>%s</td>' % (row_class, result_repr))


def results(report):
    for res in report.result_list:
        yield ResultList(None, items_for_result(report, res))

    if report.aggregate:
        aggregation_row = []
        for field in report.grouper.group_value:
            aggregation_row.append(mark_safe(u'<td>%s</td>' % "&nbsp"))
        for title, value in report.get_aggregation():
            result_repr = "%s: %s" % (title, value)
            aggregation_row.append(
                mark_safe(u'<td><strong>%s</strong></td>' % result_repr))
        yield ResultList(None, aggregation_row)


@register.inclusion_tag("admin/change_list_results.html")
def report_result_list(report):
    headers = list(result_headers(report))
    num_sorted_fields = 0
    for h in headers:
        if h['sortable'] and h['sorted']:
            num_sorted_fields += 1
    return {'cl': report,
            'result_hidden_fields': [],
            'result_headers': headers,
            'num_sorted_fields': num_sorted_fields,
            'results': list(results(report))}


@register.inclusion_tag("reporting/grouping.html")
def report_grouping(report):
    grouping_choices = []

    for choice in report.grouper.choices(report):
        grouping_choices.append(choice.values())
    return {'grouping_choices': grouping_choices}
