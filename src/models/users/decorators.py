from functools import wraps

from flask import session, url_for, request
from werkzeug.utils import redirect
import src.app


def require_login(func):
    @wraps(func)
    def requires_login_function(*args, **kwargs):
        if 'email' not in session.keys() or session['email'] is None:
            return redirect(url_for('users.login_user', next=request.path))
        return func(*args, **kwargs)
    return requires_login_function


def requires_admin_permissions(func):
    @wraps(func)
    def requires_admin_permissions_function(*args, **kwargs):
        if 'email' not in session.keys() or session['email'] is None:
            return redirect(url_for('users.login_user', next=request.path))
        if session['email'] not in src.app.app.config['ADMINS']:
            return redirect(url_for('users.login_user', message="You need to be an admin to access that"))
        return func(*args, **kwargs)
    return requires_admin_permissions_function
