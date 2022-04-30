""" common procedures and validation methods for input data """

from core_platform.utils.constants import *

from core_platform.utils.db_commands import *


def is_valid_text_field(field_value):
    """ input validation for text fields """

    if field_value is None or field_value.isspace() or len(field_value) < 1 \
            or len(field_value) > TEXT_INPUT_CHARACTER_LIMIT:
        return False
    return True


def is_valid_drop_down_field(field_value, acceptable_values):
    """ input validation for dropdown fields """

    if field_value is None or field_value not in acceptable_values:
        return False
    return True


def get_check_box_value(check_box):
    """ get check box value as a boolean """

    if check_box is not None and check_box == 'True':
        return True
    return False


def clean_doc_of_stop_words(doc):
    """ remove stopwords from nlp doc """

    clean_token = []
    for token in doc:
        if not token.is_stop:
            clean_token.append(token.text)
    if len(clean_token) < 1:
        clean_token = ["NO", "DESCRIPTION"]
    return ' '.join(clean_token)


def clean_text_of_stop_words(text):
    """ remove stop words from a text string """

    return clean_doc_of_stop_words(NLP(text))


def perform_manual_status_change(new_status, old_status, ticket_id, user_id):
    """ change status to new value """

    if is_valid_drop_down_field(new_status, DB_TICKET_STATUS_VALUE) and new_status != old_status:
        insert_action_into_db(ticket_id, CHANGED_STATUS_ACTION, new_status, user_id)
        set_ticket_status_in_db(new_status, ticket_id)
        set_ticket_update_time_to_now(ticket_id)
        return True
    return False


def perform_manual_priority_change(new_priority, old_priority, ticket_id, user_id):
    """ change priority to new value """

    if is_valid_drop_down_field(new_priority, DB_TICKET_PRIORITY_VALUE) and new_priority != old_priority:
        insert_action_into_db(ticket_id, CHANGED_PRIORITY_ACTION, new_priority, user_id)
        set_ticket_priority_in_db(new_priority, ticket_id)
        set_ticket_update_time_to_now(ticket_id)
        return True
    return False


def perform_manual_category_change(new_category, old_category, new_category_name, ticket_id, user_id):
    """ change category to new value """

    if new_category != old_category:
        insert_action_into_db(ticket_id, CHANGED_CATEGORY_ACTION, new_category_name, user_id)
        set_ticket_category_in_db(new_category, ticket_id)
        set_ticket_update_time_to_now(ticket_id)
        return True
    return False


def perform_manual_assignee_change(new_assignee_id, old_assignee, new_assignee_user, ticket_id, user_id):
    """ change assignee to new user """

    if new_assignee_id != old_assignee and new_assignee_id is not None:
        insert_action_into_db(ticket_id, CHANGED_ASSIGNEE_ACTION, new_assignee_user, user_id)
        set_ticket_assignee_in_db(new_assignee_id, ticket_id)
        if get_individual_ticket_for_edit(ticket_id)[DB_TICKET_FIELD_NAMES[4]] == DB_TICKET_STATUS_VALUE[0]:
            set_ticket_status_in_db(DB_TICKET_STATUS_VALUE[1], ticket_id)
        set_ticket_update_time_to_now(ticket_id)
        return True
    return False


def perform_solution_feedback(content, solution_status, new_ticket_status, action_id, ticket_id, user_id):
    """ update ticket based on solution feedback """

    if content is not None and solution_status is not None and new_ticket_status is not None:
        insert_action_into_db(ticket_id, PROVIDED_FEEDBACK_ACTION, content, user_id)
        change_action_type_on_ticket_action(solution_status, action_id)
        set_ticket_status_in_db(new_ticket_status, ticket_id)
        set_ticket_update_time_to_now(ticket_id)

    if PROPAGATE_SOLUTIONS and content == CONFIRMED_SOLUTION:
        unresolved_simular_ticket_ids = get_unresolved_similar_tickets_ids(ticket_id)
        action_content = get_ticket_action_by_id(action_id)['action_content']
        for sim_ticket in unresolved_simular_ticket_ids:
            if len(check_ticket_already_has_proposed_solution(action_content, sim_ticket['id'])) < 1:
                insert_action_into_db(sim_ticket['id'], PROPOSED_A_SOLUTION_ACTION, action_content, 0)
                set_ticket_status_in_db(DB_TICKET_STATUS_VALUE[3], sim_ticket['id'])
                set_ticket_update_time_to_now(sim_ticket['id'])


def extract_recommended_values(attribute_sets):
    """ finds the common values to recommend in a group of similar ticket attributes  """

    recommended_values = [None]*4

    first_attribute_set = attribute_sets[0]
    for index in range(0, len(recommended_values)):
        if all(attribute_set[index] == first_attribute_set[index] for attribute_set in attribute_sets):
            recommended_values[index] = first_attribute_set[index]
        else:
            recommended_values[index] = NO_VALUE_RECOMMENDATION_FOUND

    return recommended_values
