# -*- coding: utf-8 -*-

import reporting
from grappelli.dashboard import modules, Dashboard
from django.core.urlresolvers import reverse

class ReportLinks(modules.LinkList):

    def init_with_context(self, context):
        self.children = []
        request = context['request']
        for slug, report in reporting.user_reports(request):
            self.children.append({
                'title': report.verbose_name,
                'url': reverse('reporting-view', kwargs={'slug': slug}),
                'external': False,
            })
