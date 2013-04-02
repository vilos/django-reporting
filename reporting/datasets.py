# -*- coding: utf-8 -*-

import tablib


FORMATS = ['csv', 'html', 'json', 'ods', 'tsv', 'xls', 'xlsx', 'yaml']


class ReportDataset(tablib.Dataset):

    def __init__(self, report):
        self.report = report

        headers = self._get_headers()
        super(ReportDataset, self).__init__(headers=headers)

        self._append_data()
        self._append_aggregates()

    def _get_headers(self):
        return [self.report.result_headers[f] for f in
                self.report.list_display]

    def _append_data(self):
        for result in self.report.format_result_list(
            self.report.full_result_list):
            self.append([unicode(result[f]) for f in self.report.list_display])

    def _append_aggregates(self):
        if not self.report.aggregate:
            return

        # Initial grouper columns at left
        groupers = [''] * len(self.report.grouper.group_value)
        # Append a row of headers
        self.append(groupers + self.report.aggregate_titles)
        # Append aggregation values
        values = [unicode(value) for title, value in
                  self.report.get_aggregation()]
        self.append(groupers + values)
