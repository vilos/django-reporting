Django reporting
================

Django application for making aggregated reports in admin site

Overview
--------

This fork is completely rewritten version of original django-reporting. It's
supposed to work with Django 1.4 only and reuses admin code as much as possible.
Detail view in this version isn't supported - Django 1.4 sorting by multiple
fields makes it unnecessary.

Features
--------

* changelist like grouped reports with filters, search, pagination, etc.
* switching between different grouping field sets
* export to different data formats via tablib
* grappelli interface support

Contributors
------------

* [Lacrymology](https://github.com/Lacrymology)
* [buzanov](https://github.com/buzanov)
* [ricobl](https://github.com/ricobl)
