""" tests for user authentication """

import pytest
from flask import g, session
from core_platform.db.db_manager import get_db


def test_register(client, app):
    """ test user creation """

    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'new_user', 'password': 'new_password'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'test_user'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test_user', 'test_password', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    """ test user validation of user registration inputs """

    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    """ test user login  """

    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test_user'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test_user', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    """ test user login validation """

    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    """ test logout """

    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
