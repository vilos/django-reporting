# -*- coding: utf-8 -*-

from django.db.models import signals
from django.contrib.auth import models as auth_app
from reporting import autodiscover, all_reports, models as reportapp


def create_permissions(app, created_models, verbosity, **kwargs):
    from django.contrib.contenttypes.models import ContentType

    autodiscover()
    reports = all_reports()

    # This will hold the permissions we're looking for as
    # (content_type, (codename, name))
    searched_perms = list()
    ctype = ContentType.objects.get_for_model(auth_app.User)
    for slug, report in reports:
        for perm in report.permissions:
            searched_perms.append((ctype, perm))

    # Find all the Permissions that have a context_type for a model we're
    # looking for.  We don't need to check for codenames since we already have
    # a list of the ones we're going to create.
    all_perms = set(auth_app.Permission.objects.filter(
        content_type=ctype,
    ).values_list(
        "content_type", "codename"
    ))

    objs = [
        auth_app.Permission(codename=codename, name=name, content_type=ctype)
        for ctype, (codename, name) in searched_perms
        if (ctype.pk, codename) not in all_perms
    ]
    auth_app.Permission.objects.bulk_create(objs)
    if verbosity >= 2:
        for obj in objs:
            print "Adding permission '%s'" % obj


signals.post_syncdb.connect(create_permissions, sender=reportapp)
