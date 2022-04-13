""" test for dashboard views """


def test_index(client, auth):
    """ test index page content with and without user session """

    response = client.get('/')
    assert b"Log In" in response.data
    assert b"/auth/register" in response.data
    assert b"Create an account (register) and Log in to access content" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'<title>INDEX</title>' in response.data
    assert b'Current User:' in response.data
