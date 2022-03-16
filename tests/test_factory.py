from core_platform import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_healthcheck(client):
    response = client.get('/healthcheck')
    assert response.data == b'{"Server Status":"online"}\n'
