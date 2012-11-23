from django.db.models import Count


def DistinctCount(field):
    return Count(field, distinct=True)
