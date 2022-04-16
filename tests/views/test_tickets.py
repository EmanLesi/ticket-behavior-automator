""" tests for ticket views"""

import pytest
from core_platform.db.db_manager import get_db
from core_platform.utils.constants import *
from core_platform.utils.db_commands import get_ticket_similarities_for_view, get_ticket_actions_for_view


def test_ticket_index_with_tickets(client, app):
    """ test list view of all tickets """

    response = client.get('/ticket/')
    assert response.status_code == 200
    assert b"""<a href="/ticket/1/edit">#1 </a>""" in response.data


def test_ticket_index_with_no_tickets(client, app):
    """ test list view of all tickets when there are no tickets """

    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM ticket")
        db.commit()

    response = client.get('/ticket/')
    assert response.status_code == 200
    assert b"<p> There are no tickets in the system </p>" in response.data
    assert b"<h1>Ticket Index</h1>" in response.data


def test_create_ticket_get_page(client, auth, app):
    """ test for retrieval of ticket creation page (GET -  retrieve page) """

    auth.login()

    response = client.get('ticket/create_ticket')
    assert response.status_code == 200
    assert b"<h1>Create New Ticket</h1>" in response.data
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
    assert b"""<sub> Ticket ID: #3</sub>""" in response.data


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
                           f"AND action_type = '{MADE_A_COMMENT_ACTION}'",
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
                           f"AND action_type = '{PROPOSED_A_SOLUTION_ACTION}'",
                           (message_content,)).fetchall()
        assert len(count) == expected_response_content


def test_delete_ticket_on_existing_ticket(client, auth, app):
    """ test deleting a ticket that exists """

    auth.login()

    ticket_view_response = client.get('/ticket/2/edit')
    assert ticket_view_response.status_code == 200
    assert b'<sub> Ticket ID: #2</sub>' in ticket_view_response.data

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
        (RESOLVED_BY_PROPOSED_SOLUTION, "SELECT id FROM ticket_action WHERE ticket = 2 "
                                        f"AND action_type = '{PROVIDED_RESOLUTION_ACTION}'", 1),
        (PROPOSED_SOLUTION_INEFFECTIVE, "SELECT status FROM ticket WHERE id = 2 "
                                        f"AND status = '{DB_TICKET_STATUS_VALUE[4]}'", 1),
        (None, f"SELECT status FROM ticket WHERE id = 2 AND status = '{DB_TICKET_STATUS_VALUE[3]}'", 1),
        ('select feedback', f"SELECT status FROM ticket WHERE id = 2 AND status = '{DB_TICKET_STATUS_VALUE[3]}'", 1)
))
def test_solution_feedback(client, auth, app, feedback, test_query, expected_outcome):
    """ test feedback solution feedback system """

    auth.login()
    response = client.post('ticket/2/solution_feedback', data={'solution_feedback': feedback})
    with app.app_context():
        db = get_db()
        count = db.execute(test_query, ).fetchall()
        assert len(count) == expected_outcome
        assert response.status_code == 302
        assert b'>/ticket/2/edit</a>' in response.data


def test_delete_actions_on_existing_ticket(client, auth, app):
    """ test deleting actions on a ticket that exists """

    auth.login()

    ticket_view_response = client.get('/ticket/1/edit')
    assert ticket_view_response.status_code == 200
    assert b'<sub> Ticket ID: #1</sub>' in ticket_view_response.data

    with app.app_context():
        response = client.post('/ticket/5/delete_action/1')
        db = get_db()
        count = db.execute("SELECT id FROM ticket_action WHERE id = 1").fetchall()
        assert len(count) == 0
        assert response.status_code == 302
        assert b'>/ticket/5/edit</a>' in response.data


def test_delete_actions_on_none_existing_ticket(client, auth, app):
    """ test deleting actions on a ticket that does not exist """

    auth.login()

    ticket_view_response = client.get('/ticket/1/edit')
    assert ticket_view_response.status_code == 200
    assert b'<sub> Ticket ID: #1</sub>' in ticket_view_response.data

    with app.app_context():
        response = client.post('/ticket/999/delete_action/1')
        db = get_db()
        count = db.execute("SELECT id FROM ticket_action WHERE id = 1").fetchall()
        assert len(count) == 1
        assert response.status_code == 302
        assert b'>/ticket/</a>' in response.data


@pytest.mark.parametrize(('apply_actions', 'expected_content'), (
        (True, 2),
        (None, 0)
))
def test_reassess_similarity(client, auth, app, apply_actions, expected_content):
    """ test the requesting of a ticket to be reassessed for similarities """

    auth.login()
    response = client.post('ticket/1/reassess_similarity', data={'apply_actions': apply_actions})
    assert response.status_code == 302
    assert b'>/ticket/1/edit</a>' in response.data
    with app.app_context():
        assert len(get_ticket_similarities_for_view(1)) == 1
        assert len(get_ticket_actions_for_view(1)) == expected_content
