""" test for common procedures """
import pytest

from core_platform.utils.procedures import *


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
        (None, DB_TICKET_STATUS_VALUE, False),
        ('select new test', DB_TICKET_STATUS_VALUE, False),
        ('closed', DB_TICKET_STATUS_VALUE, True)
))
def test_is_valid_drop_down_field(value, field_name, expected_outcome):
    """ tests for dropdown input validation  """

    assert is_valid_drop_down_field(value, field_name) == expected_outcome


@pytest.mark.parametrize(('value', 'expected_outcome'), (
        ('True', True),
        ('False', False),
        (None, False),
))
def test_get_check_box_value(value, expected_outcome):
    """ tests for check input value extraction """

    assert get_check_box_value(value) == expected_outcome


@pytest.mark.parametrize(('value', 'expected_outcome'), (
        ('there are stop words in this string', 'stop words string'),
        ('there are stop words, punctuation, and spling error in this string!',
         'stop words , punctuation , spling error string !'),
))
def test_clean_doc_of_stop_words(value, expected_outcome):
    """ tests for removal of stop words from NLP doc """

    assert clean_doc_of_stop_words(NLP(value)) == expected_outcome


@pytest.mark.parametrize(('value', 'expected_outcome'), (
        ('there are stop words in this string', 'stop words string'),
        ('there are stop words, punctuation, and spling error in this string!',
         'stop words , punctuation , spling error string !'),
))
def test_clean_text_of_stop_words(value, expected_outcome):
    """ tests for removal of stop words from string """

    assert clean_text_of_stop_words(value) == expected_outcome


@pytest.mark.parametrize(('value', 'expected_outcome', 'action_count_increment'), (
        (DB_TICKET_STATUS_VALUE[5], DB_TICKET_STATUS_VALUE[5], 1),
        (DB_TICKET_STATUS_VALUE[0], DB_TICKET_STATUS_VALUE[0], 0),
        ("select new status", DB_TICKET_STATUS_VALUE[0], 0),
        ("status", DB_TICKET_STATUS_VALUE[0], 0)
))
def test_perform_manual_status_change(app, value, expected_outcome, action_count_increment):
    """ test procedure to change ticket status """

    with app.app_context():
        old_status = get_individual_ticket_for_edit(1)['status']
        old_ticket_actions = get_ticket_actions_for_view(1)

        perform_manual_status_change(value, old_status, 1, 0)

        new_status = get_individual_ticket_for_edit(1)['status']
        new_ticket_actions = get_ticket_actions_for_view(1)
        assert new_status == expected_outcome
        assert len(new_ticket_actions) == len(old_ticket_actions) + action_count_increment


@pytest.mark.parametrize(('value', 'expected_outcome', 'action_count_increment'), (
        (DB_TICKET_PRIORITY_VALUE[4], DB_TICKET_PRIORITY_VALUE[4], 1),
        (DB_TICKET_PRIORITY_VALUE[0], DB_TICKET_PRIORITY_VALUE[0], 0),
        ("select new priority", DB_TICKET_PRIORITY_VALUE[0], 0),
        ("priority", DB_TICKET_PRIORITY_VALUE[0], 0)
))
def test_perform_manual_priority_change(app, value, expected_outcome, action_count_increment):
    """ test procedure to change ticket priority """

    with app.app_context():
        old_priority = get_individual_ticket_for_edit(1)['priority']
        old_ticket_actions = get_ticket_actions_for_view(1)

        perform_manual_priority_change(value, old_priority, 1, 0)

        new_priority = get_individual_ticket_for_edit(1)['priority']
        new_ticket_actions = get_ticket_actions_for_view(1)
        assert new_priority == expected_outcome
        assert len(new_ticket_actions) == len(old_ticket_actions) + action_count_increment


@pytest.mark.parametrize(('value', 'action_count_increment'), (
        (2, 1),
        (3, 0)
))
def test_perform_manual_category_change(app, value, action_count_increment):
    """ test procedure to change ticket category """

    with app.app_context():
        old_category = get_individual_ticket_for_edit(2)['category']
        old_ticket_actions = get_ticket_actions_for_view(2)
        category_name = get_name_of_category(value)

        perform_manual_category_change(value, old_category, category_name['name'], 2, 0)

        new_category = get_individual_ticket_for_edit(2)['category']
        new_ticket_actions = get_ticket_actions_for_view(2)
        assert new_category == value
        assert len(new_ticket_actions) == len(old_ticket_actions) + action_count_increment


@pytest.mark.parametrize(('ticket_id', 'value', 'new_status', 'action_count_increment'), (
        (1, 2, DB_TICKET_STATUS_VALUE[1], 1),
        (3, 3, DB_TICKET_STATUS_VALUE[2], 1),
        (3, 2, DB_TICKET_STATUS_VALUE[2], 0),
))
def test_perform_manual_assignee_change(app, ticket_id, value, new_status, action_count_increment):
    """ test procedure to change ticket assignee """

    with app.app_context():
        old_assignee = get_individual_ticket_for_edit(ticket_id)['assignee']
        old_ticket_actions = get_ticket_actions_for_view(ticket_id)
        assignee_name = get_username_from_id(value)['username']

        perform_manual_assignee_change(value, old_assignee, assignee_name, ticket_id, 0)

        new_ticket = get_individual_ticket_for_edit(ticket_id)
        new_ticket_actions = get_ticket_actions_for_view(ticket_id)
        assert new_ticket['assignee'] == value
        assert new_ticket['status'] == new_status
        assert len(new_ticket_actions) == len(old_ticket_actions) + action_count_increment


@pytest.mark.parametrize(('content', 'solution_status', 'new_ticket_status', 'expected_outcome_sim_ticket'), (
                                 (CONFIRMED_SOLUTION, PROVIDED_RESOLUTION_ACTION, DB_TICKET_STATUS_VALUE[5],
                                  PROPOSED_A_SOLUTION_ACTION),
                                 (REJECTED_SOLUTION, PROPOSED_A_SOLUTION_ACTION, DB_TICKET_STATUS_VALUE[4],
                                  CHANGED_STATUS_ACTION),
                         ))
def test_perform_solution_feedback(app, content, solution_status, new_ticket_status, expected_outcome_sim_ticket):
    """ test update of ticket based on solution feedback """

    with app.app_context():
        solution_action = get_most_recent_solution(2)

        perform_solution_feedback(content, solution_status, new_ticket_status, solution_action['id'], 2, 1)

        assert get_ticket_action_by_id(solution_action['id'])['action_type'] == solution_status
        if content != REJECTED_SOLUTION:
            assert get_ticket_action_by_id(get_most_recent_solution(1)['id'])['action_type'] ==\
                   expected_outcome_sim_ticket


@pytest.mark.parametrize(('attribute_sets', 'expected_outcome'), (
        ([["assigned", "high", "Off Center Items", "test_user"],
          ["assigned", "high", "None", "another_user"],
          ["assigned", "high", "None", "another_user"]],
         ["assigned", "high", NO_VALUE_RECOMMENDATION_FOUND, NO_VALUE_RECOMMENDATION_FOUND]),
        ([["assigned", "high", "Off Center Items", "another_user"], ["New", "none", "None", "None"]],
         [NO_VALUE_RECOMMENDATION_FOUND, NO_VALUE_RECOMMENDATION_FOUND, NO_VALUE_RECOMMENDATION_FOUND,
          NO_VALUE_RECOMMENDATION_FOUND]),
        ([["assigned", "high", "Off Center Items", "another_user"]],
         ["assigned", "high", "Off Center Items", "another_user"]),
))
def test_extract_recommended_values(attribute_sets, expected_outcome):
    """ test extraction of common values from a group of attribute sets """

    assert extract_recommended_values(attribute_sets) == expected_outcome
