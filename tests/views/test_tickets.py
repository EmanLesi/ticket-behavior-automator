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
    assert b"<p> No Tickets Were Found </p>" in response.data
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
        assert b"""<a href="/ticket/">/ticket/</a>""" in response.data


def test_delete_ticket_on_non_existing_ticket(client, auth, app):
    """ test deleting a ticket that does not exist """

    auth.login()
    # expected to return 404 because ticket does not exist
    ticket_view_response = client.get('/ticket/999/edit')
    assert ticket_view_response.status_code == 404

    response = client.post('ticket/999/delete')
    assert response.status_code == 302
    assert b"""<a href="/ticket/">/ticket/</a>""" in response.data


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
        assert b"""<a href="/ticket/2/edit">/ticket/2/edit</a>""" in response.data


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
        assert b"""<a href="/ticket/5/edit">/ticket/5/edit</a>""" in response.data


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
        assert b"""<a href="/ticket/">/ticket/</a>""" in response.data


@pytest.mark.parametrize(('apply_actions', 'expected_content'), (
        (True, 2),
        (None, 0)
))
def test_reassess_similarity(client, auth, app, apply_actions, expected_content):
    """ test the requesting of a ticket to be reassessed for similarities """

    auth.login()
    response = client.post('ticket/1/reassess_similarity', data={'apply_actions': apply_actions})
    assert response.status_code == 302
    assert b"""<a href="/ticket/1/edit">/ticket/1/edit</a>""" in response.data
    with app.app_context():
        assert len(get_ticket_similarities_for_view(1)) == 1
        assert len(get_ticket_actions_for_view(1)) == expected_content


@pytest.mark.parametrize('query_data', (
        (['title', '', 'creation_time', 'DESC']),
        (['title', 'This is the first of many tickets', 'status', 'ASC']),
        (['title', None, 'title', 'DESC']),
        (['priority', 'none', 'update_time', 'ASC']),
))
def test_query_sorting(client, auth, app, query_data):
    """ test querying to display tickets in specified order """

    with app.app_context():
        response = client.post('/ticket/query/',
                               data={'query_field': query_data[0],
                                     'query_value': query_data[1],
                                     'query_order_field': query_data[2],
                                     'query_order_value': query_data[3],
                                     })
        assert response.status_code == 200
        assert b"""<a href="/ticket/1/edit">#1 </a>""" in response.data
        assert b"<h1>Ticket Index</h1>" in response.data


@pytest.mark.parametrize(('query_data', 'status_code', 'expected_outcome'), (
        ([None, None, None, None], 302, b"""<a href="/ticket/">/ticket/</a>"""),
        (['not a field', 'This is the first of many tickets', 'status', 'DESC'], 200,
         b"""<a href="/ticket/1/edit">#1 </a>"""),
        (['assignee', None, 'title', 'DESC'], 200, b"""<a href="/ticket/1/edit">#1 </a>"""),
        (['reporter', 'not a user', 'update_time', 'ASC'], 200, bytes(NOT_A_USER.format('not a user'), 'utf-8')),
        (['category', 'not a category', 'creation_time', 'DESC'], 200,
         bytes(NOT_A_CATEGORY.format('not a category'), 'utf-8')),
        (['priority', 'not a priority', 'status', 'ASC'], 200, b"<p> No Tickets Were Found </p>"),
        (['status', 'new', 'title', 'no order'], 302, b"""<a href="/ticket/">/ticket/</a>"""),
        (['priority', 'none', 'not order field', 'ASC'], 302, b"""<a href="/ticket/">/ticket/</a>""")
))
def test_query_invalid_criteria(client, auth, app, query_data, status_code, expected_outcome):
    """ test querying with invalid criteria """

    with app.app_context():
        response = client.post('/ticket/query/',
                               data={'query_field': query_data[0],
                                     'query_value': query_data[1],
                                     'query_order_field': query_data[2],
                                     'query_order_value': query_data[3],
                                     })
        assert response.status_code == status_code
        assert expected_outcome in response.data


@pytest.mark.parametrize('query_data', (
        (['title', 'this is not a a ticket title', 'creation_time', 'DESC']),
        (['status', 'closed', 'status', 'ASC']),
        (['reporter', 'a_third_user', 'title', 'DESC']),
))
def test_query_criteria_with_no_results(client, auth, app, query_data):
    """ test querying where no tickets match criteria """

    with app.app_context():
        response = client.post('/ticket/query/',
                               data={'query_field': query_data[0],
                                     'query_value': query_data[1],
                                     'query_order_field': query_data[2],
                                     'query_order_value': query_data[3],
                                     })
        assert response.status_code == 200
        assert b"<p> No Tickets Were Found </p>" in response.data
        assert b"<h1>Ticket Index</h1>" in response.data


@pytest.mark.parametrize('query_data', (
        (['title', 'ticket', 'creation_time', 'DESC']),
        (['title', 'This is the first of many tickets', 'status', 'ASC']),
))
def test_search_tickets_for_title(client, auth, app, query_data):
    """ test querying for a ticket title """

    with app.app_context():
        response = client.post('/ticket/query/',
                               data={'query_field': query_data[0],
                                     'query_value': query_data[1],
                                     'query_order_field': query_data[2],
                                     'query_order_value': query_data[3],
                                     })
        assert response.status_code == 200
        assert b"""<a href="/ticket/1/edit">#1 </a>""" in response.data
        assert b"<h1>Ticket Index</h1>" in response.data


@pytest.mark.parametrize(('query_data', 'expected_outcome'), (
        (['category', 'Mac Scroll Issue', 'creation_time', 'DESC'], b"""<a href="/ticket/5/edit">#5 </a>"""),
        (['category', 'None', 'creation_time', 'DESC'], b"""<a href="/ticket/1/edit">#1 </a>"""),
        (['category', 'not a category', 'creation_time', 'DESC'],
         bytes(NOT_A_CATEGORY.format('not a category'), 'utf-8')),
))
def test_search_tickets_for_category(client, auth, app, query_data, expected_outcome):
    """ test querying for a ticket category """

    with app.app_context():
        response = client.post('/ticket/query/',
                               data={'query_field': query_data[0],
                                     'query_value': query_data[1],
                                     'query_order_field': query_data[2],
                                     'query_order_value': query_data[3],
                                     })
        assert response.status_code == 200
        assert expected_outcome in response.data
        assert b"<h1>Ticket Index</h1>" in response.data


@pytest.mark.parametrize(('query_data', 'expected_outcome'), (
        (['reporter', 'test_user', 'creation_time', 'DESC'], b"""<a href="/ticket/1/edit">#1 </a>"""),
        (['assignee', 'a_third_user', 'creation_time', 'DESC'], b"""<a href="/ticket/5/edit">#5 </a>"""),
        (['assignee', 'None', 'title', 'DESC'], b"""<a href="/ticket/1/edit">#1 </a>"""),
        (['reporter', 'a_forth_user', 'creation_time', 'DESC'], bytes(NOT_A_USER.format('a_forth_user'), 'utf-8')),
        (['assignee', 'a_forth_user', 'creation_time', 'DESC'], bytes(NOT_A_USER.format('a_forth_user'), 'utf-8')),
))
def test_search_tickets_for_reporter_or_assignee(client, auth, app, query_data, expected_outcome):
    """ test display tickets sorted by id in descending order """

    with app.app_context():
        response = client.post('/ticket/query/',
                               data={'query_field': query_data[0],
                                     'query_value': query_data[1],
                                     'query_order_field': query_data[2],
                                     'query_order_value': query_data[3],
                                     })
        assert response.status_code == 200
        assert expected_outcome in response.data
        assert b"<h1>Ticket Index</h1>" in response.data
