VERSION = (0, 2, 2)
__version__ = '.'.join(map(str, VERSION))


import os
if 'DJANGO_SETTINGS_MODULE' in os.environ:
    from registry import *  # NOQA
