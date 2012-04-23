# -*- coding: utf-8 -*-

from django import template
from django.utils.datastructures import SortedDict

register = template.Library()


@register.filter
def annotate_details(queryset, report):
    show_details = report.detail_list_display and report.show_details
    for row in queryset:
        row = SortedDict(row)
        row.keyOrder = report.fields
        if show_details:
            # TODO: we can do one huge query, need to profile
            row.details = report.get_details(row)
        yield row
