""" user authorisation views based on Official Flask framework documentation """

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from core_platform.db.db_manager import get_db
from core_platform.utils.constants import AUTH_LOGIN_VIEW, AUTH_REGISTER_PAGE_TEMPLATE, INDEX_VIEW, \
    AUTH_LOGIN_PAGE_TEMPLATE

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """ this view is for new users to acquire an account """

    if request.method == 'POST':

        # extract form data
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # perform presence checks on form data
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # insert user and password hash to db - Throws alert if user already exists
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for(AUTH_LOGIN_VIEW))

        flash(error)

    return render_template(AUTH_REGISTER_PAGE_TEMPLATE)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """ this view is for users to login """

    if request.method == 'POST':
        # extract form data
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # find user in db
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # compare password hash if user is found
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # Allow access if credentials are valid
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for(INDEX_VIEW))

        flash(error)

    return render_template(AUTH_LOGIN_PAGE_TEMPLATE)


@bp.before_app_request
def load_logged_in_user():
    """ this is a session check method to find existing sessions"""

    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    """ this is the view to end the current user session """

    session.clear()
    return redirect(url_for(INDEX_VIEW))


def login_required(view):
    """ This wrapper ensures that unauthorised users are redirected to the login page """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for(AUTH_LOGIN_VIEW))

        return view(**kwargs)

    return wrapped_view
