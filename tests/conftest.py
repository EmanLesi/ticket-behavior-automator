""" configuration for unit testing environment  """

import os
import tempfile

import pytest
from core_platform import create_app
from core_platform.db.db_manager import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'testing_data.sql'), 'rb') as test_data:
    _data_sql = test_data.read().decode('utf8')


@pytest.fixture
def app():
    """ app testing environment setup """

    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    """ setup for user auth tests """

    def __init__(self, client):
        self._client = client

    def login(self, username='test_user', password='test_password'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
