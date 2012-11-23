from django.contrib.auth.models import User
from django.db.models import Count


def DistinctCount(field):
    return Count(field, distinct=True)


class ReportViewer(User):
    class Meta:
        proxy = True
        permissions = (("can_view_reports", "Can view reports"),)
