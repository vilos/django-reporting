import reporting
from django.db.models import Sum, Count
from models import Person


class PersonReport(reporting.Report):
    model = Person
    verbose_name = 'Person Report'

    # Annotation fields (tupples of field, func, title)
    # example of custom title for column
    # no title - column will be "Salary Sum"
    annotate = (
        ('id', Count, 'Total'),
        ('salary', Sum),
        ('expenses', Sum),
    )

    # columns that will be aggregated (syntax the same as for annotate)
    aggregate = (
        ('id', Count, 'Total'),
        ('salary', Sum, 'Salary'),
        ('expenses', Sum, 'Expenses'),
    )

    # list of fields and lookups for group-by options
    group_by = [
        ('department', ('department__title',)),
        ('leader', ('department__leader__name',), 'Department leader'),
        ('occupation', ('occupation__title',)),
        ('dep_occup', ('department__title', 'occupation__title',),
         'Department and occupation'),
    ]

    # This are report filter options (similar to django-admin)
    list_filter = [
       'occupation',
       'country',
    ]
    ordering = ('-id_count',)

    # the same as django-admin
    date_hierarchy = 'birth_date'
    search_fields = ('department__title',)

    def salary_sum(self, dct):
        return unicode(dct['salary_sum']) + ' $'

    def expenses_sum(self, dct):
        return unicode(dct['expenses_sum']) + ' $'


# Do not forget to 'register' your class in reports
reporting.register('people', PersonReport)
