""" DB Command Tests """
import pytest

from core_platform.utils.constants import PROPOSED_A_SOLUTION_ACTION, PROVIDED_RESOLUTION_ACTION, \
    MADE_A_COMMENT_ACTION, CHANGED_PRIORITY_ACTION
from core_platform.utils.db_commands import *


def test_fetchall_tickets_for_index(app):
    """ test the retrial of all tickets and associated values from other tables in db """

    with app.app_context():
        db_output = fetchall_tickets_for_index()
        assert len(db_output) == 10
        assert db_output[0]['id'] == 10


def test_get_individual_ticket_for_edit(app):
    """ test the retrieval of a specific ticket from db """

    with app.app_context():
        db_output = get_individual_ticket_for_edit(1)
        assert db_output['status'] == DB_TICKET_STATUS_VALUE[0]


def test_get_individual_ticket_for_view(app):
    """ test the retrieval of a specific ticket and associated values from other tables in db """

    with app.app_context():
        db_output = get_individual_ticket_for_view(1)
        assert db_output['priority'] == DB_TICKET_PRIORITY_VALUE[0]
        assert db_output['status'] == DB_TICKET_STATUS_VALUE[0]


def test_get_individual_ticket_for_sim_analysis(app):
    """ test getting ticket fields for individual ticket that is required for NLP analysis """

    with app.app_context():
        db_output = get_individual_ticket_for_sim_analysis(1)
        assert db_output['id'] == 1


def test_get_ticket_actions_for_view(app):
    """ test the retrieval of all actions performed on ticket """

    with app.app_context():
        db_output = get_ticket_actions_for_view(3)
        assert len(db_output) == 5


def test_get_all_other_ticket_titles_and_descriptions(app):
    """ test the getting of the titles and descriptions of other tickets  """

    with app.app_context():
        db_output = get_all_other_ticket_titles_and_descriptions(1)
        assert len(db_output) == 9
        assert db_output[0]['id'] == 2


def test_get_ticket_reporter(app):
    """ test getting the reporter id of a specific ticket """

    with app.app_context():
        db_output = get_ticket_reporter(1)
        assert db_output['reporter'] == 1


def test_get_most_recent_solution(app):
    """ test getting the most recent solution to a ticket """

    with app.app_context():
        db_output = get_most_recent_solution(2)
        assert db_output['id'] == 17


def test_get_all_solutions_from_tickets(app):
    """ test getting all proposed solutions from a group of tickets """

    with app.app_context():
        db_output = get_all_solutions_from_tickets('1,2,3')
        assert len(db_output) == 1
        assert db_output[0]['action_type'] == PROPOSED_A_SOLUTION_ACTION


def test_get_unresolved_similar_tickets_ids(app):
    """ test get ids simular unresolved tickets to a ticket """

    with app.app_context():
        db_output = get_unresolved_similar_tickets_ids(8)
        assert len(db_output) == 3
        assert db_output[0]['id'] == 9


def test_get_ticket_id(app):
    """ test verification of a ticket existing in database """

    with app.app_context():
        db_output = get_ticket_id(3)
        assert db_output['id'] == 3


def test_get_ticket_id_of_non_existent_ticket(app):
    """ test verification of a ticket that does not exist in database """

    with app.app_context():
        db_output = get_ticket_id(999)
        assert db_output is None


def test_get_ticket_similarities_for_view(app):
    """ test getting the similar tickets for specific ticket """

    with app.app_context():
        db_output = get_ticket_similarities_for_view(2)
        assert len(db_output) == 1


def test_get_all_registered_users(app):
    """ test retrieval of all usernames in db """

    with app.app_context():
        db_output = get_all_registered_users()
        assert len(db_output) == 3


def test_get_all_category_names(app):
    """ test retrieval of all category names in db """

    with app.app_context():
        db_output = get_all_category_names()
        assert len(db_output) == 3


def test_get_username_from_id(app):
    """ test getting the username from id """

    with app.app_context():
        db_output = get_username_from_id(1)
        assert db_output['username'] == 'test_user'


def test_get_id_of_user(app):
    """ test getting id from username """

    with app.app_context():
        db_output = get_id_of_user('test_user')
        assert db_output['id'] == 1


def test_get_id_of_category(app):
    """ test getting id from category name """

    with app.app_context():
        db_output = get_id_of_category("Category That Exists")
        assert db_output['id'] == 3


def test_get_id_of_non_existent_category(app):
    """ test getting id from category name that does not exist """

    with app.app_context():
        db_output = get_id_of_category("category that does not exist")
        assert db_output is None


@pytest.mark.parametrize(('value', 'expected_value'),
                         ((3, "Category That Exists"), (999, DB_CATEGORY_NONE_NAME)))
def test_get_name_of_category(app, value, expected_value):
    """ test getting name from category id """

    with app.app_context():
        db_output = get_name_of_category(value)
        assert db_output['name'] == expected_value


def test_get_id_of_the_newest_ticket(app):
    """ test getting the id of the last ticket that was created in the db """

    with app.app_context():
        db_output = get_id_of_the_newest_ticket()
        assert db_output['id'] == 10


def test_insert_new_ticket_into_db(app):
    """ test inserting new ticket in to db """

    with app.app_context():
        old_latest_ticket_id = get_id_of_the_newest_ticket()['id']
        db_output = insert_new_ticket_into_db("Title of new ticket", "description of new ticket", 1, 1)
        assert db_output == DB_SUCCESS

        new_latest_ticket_id = get_id_of_the_newest_ticket()['id']
        assert old_latest_ticket_id < new_latest_ticket_id
        new_ticket = get_individual_ticket_for_edit(new_latest_ticket_id)
        assert new_ticket['status'] == DB_TICKET_STATUS_VALUE[0]


def test_insert_action_into_db(app):
    """ test recording actions being performed on tickets """

    with app.app_context():
        assert get_ticket_action_by_id(20) is None
        insert_action_into_db(1, MADE_A_COMMENT_ACTION, "new action to find", 1)
        db_output = get_ticket_action_by_id(20)
        assert db_output['action_type'] == MADE_A_COMMENT_ACTION
        assert db_output['action_content'] == "new action to find"


def test_get_ticket_action_by_id(app):
    """ test retrieval of action by id """

    with app.app_context():
        db_output = get_ticket_action_by_id(1)
        assert db_output['action_type'] == CHANGED_PRIORITY_ACTION
        assert db_output['action_content'] == "medium"


def test_check_ticket_already_has_proposed_solution(app):
    """ test find proposed solution on a ticket based on its action content """

    with app.app_context():
        db_output = check_ticket_already_has_proposed_solution("this is a test solution", 2)
        assert db_output is not None
        assert db_output[0]['id'] == 17


def test_set_ticket_update_time_to_now(app):
    """ test updating of a ticket's update time """

    with app.app_context():
        old_update_time = get_individual_ticket_for_view(1)['update_time']
        set_ticket_update_time_to_now(1)
        new_update_time = get_individual_ticket_for_view(1)['update_time']
        assert old_update_time != new_update_time
        assert old_update_time < new_update_time


def test_set_ticket_status_in_db(app):
    """ test setting ticket status in db """

    with app.app_context():
        old_status = get_individual_ticket_for_edit(1)['status']
        set_ticket_status_in_db(DB_TICKET_STATUS_VALUE[5], 1)
        new_status = get_individual_ticket_for_edit(1)['status']
        assert old_status != new_status
        assert new_status == DB_TICKET_STATUS_VALUE[5]


def test_set_ticket_priority_in_db(app):
    """ test setting ticket priority in db """

    with app.app_context():
        old_priority = get_individual_ticket_for_edit(1)['priority']
        set_ticket_priority_in_db(DB_TICKET_PRIORITY_VALUE[1], 1)
        new_priority = get_individual_ticket_for_edit(1)['priority']
        assert old_priority != new_priority
        assert new_priority == DB_TICKET_PRIORITY_VALUE[1]


def test_set_ticket_category_in_db(app):
    """ test setting ticket category in db """

    with app.app_context():
        old_category = get_individual_ticket_for_edit(1)['category']
        set_ticket_category_in_db(2, 1)
        new_category = get_individual_ticket_for_edit(1)['category']
        assert old_category != new_category
        assert new_category == 2


def test_set_ticket_assignee_in_db(app):
    """ test setting ticket assignee in db """

    with app.app_context():
        old_assignee = get_individual_ticket_for_edit(1)['assignee']
        set_ticket_assignee_in_db(1, 1)
        new_assignee = get_individual_ticket_for_edit(1)['assignee']
        assert old_assignee != new_assignee
        assert new_assignee == 1


def test_insert_new_category(app):
    """ test inserting new category into db """

    with app.app_context():
        assert get_id_of_category("new category") is None
        insert_new_category("new category")
        assert get_id_of_category("new category")['id'] == 4


def test_change_action_type_on_ticket_action(app):
    """ test changing action type on ticket action """

    with app.app_context():
        assert get_ticket_action_by_id(17)['action_type'] == PROPOSED_A_SOLUTION_ACTION
        change_action_type_on_ticket_action(PROVIDED_RESOLUTION_ACTION, 17)
        assert get_ticket_action_by_id(17)['action_type'] == PROVIDED_RESOLUTION_ACTION


def test_delete_action_from_ticket(app):
    """ test deletion of action from ticket actions """

    with app.app_context():
        assert get_ticket_action_by_id(1) is not None
        delete_action_from_ticket(5, 1)
        assert get_ticket_action_by_id(1) is None


def test_delete_all_associated_with_ticket(app):
    """ test deletion of every data point associated with a ticket """

    with app.app_context():
        assert get_ticket_id(5)['id'] == 5
        assert len(get_ticket_actions_for_view(5)) > 0
        delete_all_associated_with_ticket(5)
        assert get_ticket_id(5) is None
        assert len(get_ticket_actions_for_view(5)) == 0


def test_delete_ticket_similarities_for_ticket(app):
    """ test deletion similarities for ticket """

    with app.app_context():
        assert len(get_ticket_similarities_for_view(8)) > 0
        delete_ticket_similarities_for_ticket(8)
        assert len(get_ticket_similarities_for_view(8)) == 0


def test_insert_ticket_similarity(app):
    """ test dding ticket similarity value to db """

    with app.app_context():
        assert len(get_ticket_similarities_for_view(1)) == 0
        insert_ticket_similarity(1, 2, 0.954, 0.844)
        assert len(get_ticket_similarities_for_view(1)) == 1
