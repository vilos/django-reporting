from django.contrib.auth.models import User


class ReportViewer(User):
    class Meta:
        proxy = True
        permissions = (("can_view_reports", "Can view reports"),)
