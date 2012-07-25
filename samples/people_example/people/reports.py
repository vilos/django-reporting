import reporting
from django.db.models import Sum, Avg, Count
from models import Person

class PersonReport(reporting.Report):
    model = Person
    verbose_name = 'Person Report'
    annotate = (                    # Annotation fields (tupples of field, func, title)
        ('id', Count, 'Total'),     # example of custom title for column
        ('salary', Sum),            # no title - column will be "Salary Sum"
        ('expenses', Sum),
    )
    aggregate = (                   # columns that will be aggregated (syntax the same as for annotate)
        ('id', Count, 'Total'),
        ('salary', Sum, 'Salary'),
        ('expenses', Sum, 'Expenses'),
    )
    group_by = [                   # list of fields and lookups for group-by options
        ('department', ('department__title',)),
        ('leader', ('department__leader__name',), 'Department leader'),
        ('occupation', ('occupation__title',)),
        ('dep_occup', ('department__title', 'occupation__title',), 'Department and occupation'),
    ]
    list_filter = [                # This are report filter options (similar to django-admin)
       'occupation',
       'country',
    ]
    ordering = ('-id_count',)

    date_hierarchy = 'birth_date' # the same as django-admin
    search_fields = ("department__title",)


reporting.register('people', PersonReport) # Do not forget to 'register' your class in reports
