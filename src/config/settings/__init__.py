import os

if os.environ.get('ENVIRONMENT', '') != 'prod':
    try:
        from .local import *  # noqa
    except ImportError:
        from .default import *  # noqa
else:
    from .prod import *  # noqa
