# -*- coding: utf-8 -*-

import copy

from django import forms
from django.conf import settings
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.util import get_fields_from_path
from django.contrib.admin.views.main import ORDER_VAR, ChangeList
from django.core.paginator import Paginator, InvalidPage
from django.db.models.fields import FieldDoesNotExist
# we have to check EmptyQuerySet due to
# https://code.djangoproject.com/ticket/17681
from django.db.models.query import EmptyQuerySet
from django.utils.datastructures import SortedDict
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _


GROUP_BY_VAR = 'group_by'

REPORT_IGNORED_PARAMS = (GROUP_BY_VAR,)


class ReportGrouper(object):
    parameter_name = GROUP_BY_VAR
    used_parameters = {}

    def __init__(self, request, params, report):
        group_choices = self.groupers(request, report)
        if group_choices is None:
            group_choices = ()
        self.group_choices = list(group_choices)
        groups = self.groups(request, report)
        if groups is None:
            groups = {}
        groups = dict(list(groups))
        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
        else:
            value = self.default_value()

        self.used_parameters[self.parameter_name] = value
        self.group_value = groups.get(value, groups.get(self.default_value(),
                                                        None))

    def has_output(self):
        return len(self.group_choices) > 0

    def default_value(self):
        if self.has_output():
            return self.group_choices[0][0]
        else:
            return None

    def value(self):
        return self.used_parameters.get(self.parameter_name, None)

    def groups(self, request, report):
        """ Returns groups as (value, (*group_fields)) """
        for group in report.group_by:
            yield (group[0], group[1])

    def groupers(self, request, report):
        """Returns group choices as (value, verbose_name)"""
        for group in report.group_by:
            assert isinstance(group, (list, tuple))
            assert len(group) >= 2
            if len(group) == 2:
                yield (group[0], capfirst(group[0]))
            else:
                yield (group[0], group[2])

    def expected_parameters(self):
        return [self.parameter_name]

    def choices(self, report):
        for group, title in self.group_choices:
            yield SortedDict([
                ('selected', self.value() == group),
                ('query_string', report.get_query_string({GROUP_BY_VAR: group},
                                                         [])),
                ('display', title)
            ])


class ReportAdmin(object):
    ordering = ()
    paginator = Paginator

    def __init__(self, report):
        self.report = report
        self.ordering = report.ordering

    def __getattr__(self, name):
        # pretend that report admin has all attributes from list_display
        if name in self.report.result_headers:
            f = lambda x: None
            f.short_description = self.report.result_headers[name]
            f.admin_order_field = name
            return f

    def queryset(self, request):
        return self.report.get_root_query_set(request)

    def get_ordering(self, request):
        return (self.report.fields[0],)

    def get_paginator(self, request, queryset, per_page, orphans=0,
                      allow_empty_first_page=True):
        return self.paginator(queryset, per_page, orphans,
                              allow_empty_first_page)

    def lookup_allowed(self, lookup, value):
        return True

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        js = [
            'core.js',
            'jquery%s.js' % extra,
            'jquery.init.js'
        ]
        return forms.Media(js=[static('admin/js/%s' % url) for url in js])


class Report(ChangeList):
    aggregate = ()
    annotate = ()
    detail_list_display = None
    date_hierarchy = None
    formset = None
    group_by = ()
    ordering = ()
    list_display = ()
    list_display_links = (None,)
    list_editable = False
    list_filter = ()
    list_max_show_all = 200
    list_select_related = False
    list_per_page = 100
    search_fields = ()

    def __init__(self, request):
        params = dict(request.GET.items())
        self.grouper = ReportGrouper(request, params, self)
        self.result_headers = self.get_result_headers()
        self.list_display = self.get_list_display()
        self.admin = ReportAdmin(self)

        super(Report, self).__init__(request, self.model, self.list_display,
                self.list_display_links, self.list_filter, self.date_hierarchy,
                self.search_fields, self.list_select_related,
                self.list_per_page, self.list_max_show_all, self.list_editable,
                self.admin)
        self.opts = copy.copy(self.opts)
        self.opts.verbose_name = _("row")
        self.opts.verbose_name_plural = _("rows")
        self.aggregate, self.aggregate_titles = self.split_annotate_titles(
            self.aggregate)

    def get_aggregation(self):
        if self.aggregate is None:
            return None
        aggregate_args = {}
        for field, func in self.aggregate:
            aggregate_args[field] = func(field)

        if not isinstance(self.query_set, EmptyQuerySet):
            data = self.query_set.aggregate(**aggregate_args)
        else:
            data = {}

        result = []
        ind = 0
        for field, func in self.aggregate:
            title = self.aggregate_titles[ind]
            result.append((title, data.get(field, 0)))
            ind += 1
        return result

    def get_list_display(self):
        list_display = []
        if self.grouper.has_output():
            list_display += self.grouper.group_value

        for field, annotator in self.annotate_fields:
            list_display.append(field)

        return list_display

    def get_filters(self, request):
        lookup_params = self.params

        for ignored in REPORT_IGNORED_PARAMS:
            if ignored in lookup_params:
                del lookup_params[ignored]

        return super(Report, self).get_filters(request)

    def get_ordering(self, request, queryset):
        params = self.params
        ordering = list(self._get_default_ordering())
        if ORDER_VAR in params:
            # Clear ordering and used params
            ordering = []
            order_params = params[ORDER_VAR].split('.')
            for p in order_params:
                try:
                    none, pfx, idx = p.rpartition('-')
                    field_name = self.list_display[int(idx)]
                    order_field = self.get_ordering_field(field_name)
                    if not order_field:
                        continue  # No 'admin_order_field', skip it
                    ordering.append(pfx + order_field)
                except (IndexError, ValueError):
                    continue  # Invalid ordering specified, skip it.

        # Add the given query's ordering fields, if any.
        ordering.extend(queryset.query.order_by)

        return ordering

    def get_query_string(self, new_params=None, remove=None):
        params = {GROUP_BY_VAR: self.grouper.value()}
        if new_params is not None:
            params.update(new_params)
        return super(Report, self).get_query_string(params, remove)

    def get_results(self, request):
        query_set = self.get_annotated_queryset(request)
        paginator = self.model_admin.get_paginator(request, query_set,
                                                   self.list_per_page)
        # Get the number of objects, with admin filters applied.
        result_count = paginator.count

        # Get the total number of objects, with no admin filters applied.
        # Perform a slight optimization: Check to see whether any filters were
        # given. If not, use paginator.hits to calculate the number of objects,
        # because we've already done paginator.hits and the value is cached.
        if not self.query_set.query.where:
            full_result_count = result_count
        else:
            full_result_count = self.root_query_set.count()

        can_show_all = result_count <= self.list_max_show_all
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            result_list = query_set._clone()
        else:
            try:
                result_list = paginator.page(self.page_num + 1).object_list
            except InvalidPage:
                raise IncorrectLookupParameters

        self.result_count = result_count
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator

    def get_result_headers(self):
        output = {}
        if self.grouper.has_output():
            for field in self.grouper.group_value:
                output[field] = capfirst(get_fields_from_path(
                    self.model, field)[-1].verbose_name)

        annotate, self.annotate_titles = self.split_annotate_titles(
            self.annotate)
        self.annotate_fields = self.get_annotate_fields(annotate)
        func = lambda x: x[0]
        annotate_map = dict(zip(map(func, self.annotate_fields),
                                self.annotate_titles))
        output.update(annotate_map)
        return output

    def get_annotate_fields(self, annotate):
        annotate_fields = []
        for field, func in annotate:
            key = field + "_" + func.__name__.lower()
            annotate_fields.append((key, func(field)))

        return annotate_fields

    def get_root_query_set(self, request):
        return self.model.objects.all()

    def get_annotated_queryset(self, request):
        qs = self.query_set
        if not isinstance(qs, EmptyQuerySet) and self.grouper.has_output():
            values = self.grouper.group_value
            qs = qs.values(*values)
            qs = qs.annotate(**dict(self.annotate_fields))

        return qs

    def get_lookup_title(self, lookup):
        try:
            return capfirst(self.model._meta.get_field(lookup).verbose_name)
        except FieldDoesNotExist:
            if '__' not in lookup and not hasattr(self, lookup):
                raise
            parts = lookup.split('__')
            return ', '.join([capfirst(i.replace('_', ' ')) for i in parts])

    def split_annotate_titles(self, items):
        data, titles = [], []
        for item in items:
            if len(item) == 3:
                data.append(item[:2])
                titles.append(item[-1])
            else:
                data.append(item)
                field_name = self.get_lookup_title(item[0])
                text = '%s %s' % (field_name, item[1].__name__)
                titles.append(text)
        return data, titles
