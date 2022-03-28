""" tests for ticket views"""

import pytest
from core_platform.db.db_manager import get_db
from core_platform.views.tickets import is_valid_text_field, is_valid_drop_down_field


def test_ticket_index_with_tickets(client, app):
    """ test list view of all tickets """

    response = client.get('/ticket/')
    assert response.status_code == 200
    assert b"<h1>ticket index</h1>" in response.data


def test_ticket_index_with_no_tickets(client, app):
    """ test list view of all tickets when there are no tickets """

    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM ticket")
        db.commit()

    response = client.get('/ticket/')
    assert response.status_code == 200
    assert b"<p> There are no tickets in the system </p>" in response.data
    assert b"<h1>ticket index</h1>" in response.data


@pytest.mark.parametrize(('value', 'expected_outcome'), (
        ('', False),
        (None, False),
        (' ', False),
        ('valid test value', True)
))
def test_is_valid_text_field(value, expected_outcome):
    """ tests for text field input validation  """

    assert is_valid_text_field(value) == expected_outcome


@pytest.mark.parametrize(('value', 'field_name', 'expected_outcome'), (
        (None, 'test', False),
        ('select new test', 'test', False),
        ('valid test value', 'test', True)
))
def test_is_valid_drop_down_field(value, field_name, expected_outcome):
    """ tests for dropdown input validation  """

    assert is_valid_drop_down_field(value, field_name) == expected_outcome


def test_create_ticket_get_page(client, auth, app):
    """ test for retrieval of ticket creation page (GET -  retrieve page) """

    auth.login()

    response = client.get('ticket/create_ticket')
    assert response.status_code == 200
    assert b"<h1>New Ticket</h1>" in response.data
    assert b"A description is optional but advised" in response.data


@pytest.mark.parametrize(('title', 'description', 'message', 'expected_count'), (
        ('This Ticket has a Title', 'This is ticket has a description', b'<h1>ticket index</h1>', 1),
        (None, 'This is ticket has a description', b'Title is required.', 0),
        ('', '', b'Title is required.', 0),
        ('This Ticket has a Title and no description', '', b'<h1>ticket index</h1>', 1)
))
def test_create_ticket_validation_and_creation(client, auth, app, title, description, message, expected_count):
    """ tests for ticket creation view (POST - form completed) """

    auth.login()
    with app.app_context():
        client.post(
            '/ticket/create_ticket',
            data={'title': title, 'description': description}
        )
        db = get_db()
        count = db.execute("select id FROM ticket WHERE title = ?", (title,)).fetchall()
        assert len(count) == expected_count


def test_view_existing_ticket(client, auth, app):
    """ test viewing an existing ticket """

    auth.login()
    response = client.get('ticket/3/edit')
    assert response.status_code == 200
    assert b'<h1> Ticket ID: 3</h1>' in response.data


@pytest.mark.parametrize(('message_content', 'expected_response_content',), (
        ('this is a comment with content', 1),
        (None, 0)
))
def test_make_comment(client, auth, app, message_content, expected_response_content):
    """ test making a comment on a ticket """

    auth.login()
    client.post(
        'ticket/make_comment/2/', data={'comment_action': message_content, 'solution_checkbox': False}
    )
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT associated_user FROM ticket_action WHERE ticket = 2 AND action_content = ? "
                           "AND action_type = 'MADE A COMMENT'",
                           (message_content,)).fetchall()
        assert len(count) == expected_response_content


@pytest.mark.parametrize(('message_content', 'expected_response_content',), (
        ('this is a solution comment', 1),
        (None, 0)
))
def test_make_a_solution_comment(client, auth, app, message_content, expected_response_content):
    """ test proposing a solution on a ticket """

    auth.login()
    client.post(
        'ticket/make_comment/2/', data={'comment_action': message_content, 'solution_checkbox': True}
    )
    with app.app_context():
        db = get_db()
        count = db.execute("SELECT associated_user FROM ticket_action WHERE ticket = 2 AND action_content = ? "
                           "AND action_type = 'PROPOSED A SOLUTION'",
                           (message_content,)).fetchall()
        assert len(count) == expected_response_content


def test_delete_ticket_on_existing_ticket(client, auth, app):
    """ test deleting a ticket that exists """

    auth.login()

    ticket_view_response = client.get('/ticket/2/edit')
    assert ticket_view_response.status_code == 200
    assert b'<h1> Ticket ID: 2</h1>' in ticket_view_response.data

    with app.app_context():
        response = client.post('/ticket/2/delete')
        db = get_db()
        count = db.execute("SELECT id FROM ticket WHERE id = 2").fetchall()
        assert len(count) == 0
        assert response.status_code == 302
        assert b'>/ticket/</a>' in response.data


def test_delete_ticket_on_non_existing_ticket(client, auth, app):
    """ test deleting a ticket that does not exist """

    auth.login()
    # expected to return 404 because ticket does not exist
    ticket_view_response = client.get('/ticket/999/edit')
    assert ticket_view_response.status_code == 404

    response = client.post('ticket/999/delete')
    assert response.status_code == 302
    assert b'>/ticket/</a>' in response.data


@pytest.mark.parametrize(('feedback', 'test_query', 'expected_outcome'), (
        ('resolved by proposed solution', "SELECT id FROM ticket_action WHERE ticket = 3 "
                                          "AND action_type = 'PROVIDED RESOLUTION'", 1),
        ('proposed solution was not affective', "SELECT status FROM ticket WHERE id = 3 "
                                                "AND status = 'solution ineffective'", 1),
        (None, "SELECT status FROM ticket WHERE id = 3 AND status = 'solution proposed'", 1),
        ('select feedback', "SELECT status FROM ticket WHERE id = 3 AND status = 'solution proposed'", 1)
))
def test_solution_feedback(client, auth, app, feedback, test_query, expected_outcome):
    """ test feedback solution feedback system """

    auth.login()
    response = client.post('ticket/3/solution_feedback', data={'solution_feedback': feedback})
    with app.app_context():

        db = get_db()
        count = db.execute(test_query,).fetchall()
        assert len(count) == expected_outcome
        assert response.status_code == 302
        assert b'>/ticket/3/edit</a>' in response.data


def test_delete_actions_on_existing_ticket(client, auth, app):
    """ test deleting actions on a ticket that exists """

    auth.login()

    ticket_view_response = client.get('/ticket/1/edit')
    assert ticket_view_response.status_code == 200
    assert b'<h1> Ticket ID: 1</h1>' in ticket_view_response.data

    with app.app_context():
        response = client.post('/ticket/1/delete_action/1')
        db = get_db()
        count = db.execute("SELECT id FROM ticket_action WHERE id = 1").fetchall()
        assert len(count) == 0
        assert response.status_code == 302
        assert b'>/ticket/1/edit</a>' in response.data


def test_delete_actions_on_none_existing_ticket(client, auth, app):
    """ test deleting actions on a ticket that does not exist """

    auth.login()

    ticket_view_response = client.get('/ticket/1/edit')
    assert ticket_view_response.status_code == 200
    assert b'<h1> Ticket ID: 1</h1>' in ticket_view_response.data

    with app.app_context():
        response = client.post('/ticket/999/delete_action/1')
        db = get_db()
        count = db.execute("SELECT id FROM ticket_action WHERE id = 1").fetchall()
        assert len(count) == 1
        assert response.status_code == 302
        assert b'>/ticket/</a>' in response.data
