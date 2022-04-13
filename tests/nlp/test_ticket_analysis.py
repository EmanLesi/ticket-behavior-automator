""" tests for the NLP ticket analyis """
import pytest

from core_platform.nlp.ticket_analysis import *
from core_platform.utils.constants import DB_TICKET_STATUS_VALUE
from core_platform.utils.db_commands import get_ticket_similarities_for_view, get_ticket_actions_for_view


def test_perform_ticket_analysis_with_apply_action(app):
    """test ticket sim analysis with applying actions """

    with app.app_context():
        old_ticket_similarities = get_ticket_similarities_for_view(1)
        perform_ticket_analysis(True, 1)
        new_ticket_similarities = get_ticket_similarities_for_view(1)
        assert len(old_ticket_similarities) < len(new_ticket_similarities)
        assert len(new_ticket_similarities) == 1
        assert len(get_ticket_actions_for_view(1)) == 2


def test_perform_ticket_analysis_without_apply_action(app):
    """ test ticket sim analysis without applying actions """

    with app.app_context():
        old_ticket_similarities = get_ticket_similarities_for_view(1)
        perform_ticket_analysis(False, 1)
        new_ticket_similarities = get_ticket_similarities_for_view(1)
        assert len(old_ticket_similarities) < len(new_ticket_similarities)
        assert len(new_ticket_similarities) == 1
        assert len(get_ticket_actions_for_view(1)) == 0


@pytest.mark.parametrize(('sim_ticket_ids', 'field_name', 'default', 'expected_outcome'), (
        ('3,4', 'status', DB_TICKET_STATUS_VALUE[0], DB_TICKET_STATUS_VALUE[2]),
        ('3,8,7', 'status', DB_TICKET_STATUS_VALUE[0], DB_TICKET_STATUS_VALUE[0]),
        ('3', 'assignee', 1, 2),
        ('', 'category', 3, 3),
))
def test_get_attribute_from_simular_tickets(app, sim_ticket_ids, field_name, default, expected_outcome):
    """ test retrieval of common attributes in a ticket group """

    with app.app_context():
        assert get_attribute_from_simular_tickets(sim_ticket_ids, field_name, default) == expected_outcome


@pytest.mark.parametrize(('ticket_id', 'expected_outcome'), (
        (3, 5),
        (1, 2),
))
def test_apply_actions_from_ticket_sim_analysis(app, ticket_id, expected_outcome):
    """ test the application of actions from a ticket sim analysis """

    with app.app_context():
        apply_actions_from_ticket_sim_analysis(get_sorted_ticket_sim_analysis_results(ticket_id), ticket_id)

        assert len(get_ticket_actions_for_view(ticket_id)) == expected_outcome


@pytest.mark.parametrize(('ticket_id', 'most_similar_ticket_set', 'sorted_ticket_sim_length'), (
        (3, [4, 0.9141327192151049, 0.8392676663568354], 1),
        (8, [9, 0.7689649651999618, 0.8881253182255129], 1),
        (6, None, 0)
))
def test_get_sorted_ticket_sim_analysis_results(app, ticket_id, most_similar_ticket_set, sorted_ticket_sim_length):
    """ test sorting of ticket similarity analysis results """

    with app.app_context():
        sorted_ticket_sims = get_sorted_ticket_sim_analysis_results(ticket_id)
        assert len(sorted_ticket_sims) == sorted_ticket_sim_length
        if len(sorted_ticket_sims) > 0:
            assert sorted_ticket_sims[0] == most_similar_ticket_set


@pytest.mark.parametrize(('ticket_id', 'most_similar_ticket_set', 'expected_description_flag_value'), (
        (7, [1, 0.5889191037371819, 0.6718314842165113], 0),
        (2, [1, 0.9284602531865301, 0.6822534234170715], 1),
))
def test_generate_ticket_similarities(app, ticket_id, most_similar_ticket_set, expected_description_flag_value):
    """ test the generation of ticket similarities """

    with app.app_context():
        ticket_sims, description_flag = generate_ticket_similarities(ticket_id)
        assert len(ticket_sims) == 9
        assert ticket_sims[0] == most_similar_ticket_set
        assert description_flag == expected_description_flag_value
