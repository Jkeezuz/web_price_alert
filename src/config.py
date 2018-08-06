import os

DEBUG = True
ADMINS = frozenset([
    os.environ.get('ADMIN_EMAIL')
])
APPLICATION_ROOT = '/app'
SESSION_COOKIE_PATH = '/'