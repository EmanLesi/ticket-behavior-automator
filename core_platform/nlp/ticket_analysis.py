""" automatic processing of tickets """

from core_platform.utils.procedures import *


def generate_ticket_similarities(ticket_id):
    """ analyse and extract similarity of a ticket to all other tickets """

    # get the ticket being compared to and convert it to doc
    new_ticket = get_individual_ticket_for_sim_analysis(ticket_id)

    new_ticket_title_as_doc = NLP(new_ticket['title'])
    new_ticket_desc_as_doc = NLP(clean_text_of_stop_words(new_ticket['description']))
    new_ticket_short_desc_flag = new_ticket['short_description_flag']

    # get all other tickets and convert them to docs
    tickets = get_all_other_ticket_titles_and_descriptions(new_ticket['id'])

    tickets_as_docs = []

    for row in tickets:
        if row['description'] is None:
            clean_desc_doc = DEFAULT_FOR_NO_DESCRIPTION

        else:
            clean_desc_doc = clean_text_of_stop_words(row['description'])

        tickets_as_docs.append([row['id'], NLP(row['title']), NLP(clean_desc_doc)])

    # calculate similarity values of the tickets
    ticket_similarities = []
    for ticket in tickets_as_docs:
        title_similarity = new_ticket_title_as_doc.similarity(ticket[1])
        desc_similarity = new_ticket_desc_as_doc.similarity(ticket[2])
        ticket_similarities.append([ticket[0], title_similarity, desc_similarity])

    return ticket_similarities, new_ticket_short_desc_flag


def get_sorted_ticket_sim_analysis_results(ticket_id):
    """ get and sort similarity values of tickets"""

    ticket_sims, description_status = generate_ticket_similarities(ticket_id)

    # filter out tickets side of threshold depending on description complexity
    if description_status == 1:
        gated_ticket_sims = list(filter(lambda ticket_sim: ticket_sim[1] > TITLE_SIMILARITY_THRESHOLD, ticket_sims))
        sorted_ticket_sims = sorted(gated_ticket_sims, key=lambda ticket_sim: -ticket_sim[1])
    else:
        gated_ticket_sims = list(filter(lambda ticket_sim:
                                        (ticket_sim[1] + ticket_sim[2]) > TITLE_WITH_DESC_SIMILARITY_THRESHOLD,
                                        ticket_sims))
        sorted_ticket_sims = sorted(gated_ticket_sims, key=lambda ticket_sim: -(ticket_sim[1] + ticket_sim[2]))

    # crop ticket pool to only the most similar
    if len(sorted_ticket_sims) > SIMILARITY_GROUP_SIZE:
        sorted_ticket_sims = sorted_ticket_sims[0:SIMILARITY_GROUP_SIZE]

    return sorted_ticket_sims


def apply_actions_from_ticket_sim_analysis(ticket_sims, ticket_id):
    """ apply actions from similar tickets where applicable """

    if len(ticket_sims) > 0:
        sim_ticket_ids = list(map(lambda ticket_sim: ticket_sim[0], ticket_sims))
        sim_ticket_ids = str(sim_ticket_ids)[1:-1].replace(" ", "")

        # fetch existing ticket data
        old_ticket = get_individual_ticket_for_edit(ticket_id)

        # automatically set new assignee
        new_assignee = get_attribute_from_simular_tickets(sim_ticket_ids, "assignee", None)

        perform_manual_assignee_change(new_assignee, old_ticket['assignee'],
                                       get_username_from_id(new_assignee)['username'], ticket_id, 0)

        # automatically set new status
        new_status = get_attribute_from_simular_tickets(sim_ticket_ids, "status", old_ticket['status'])
        if new_status == DB_TICKET_STATUS_VALUE[5]:
            new_status = old_ticket['status']
        perform_manual_status_change(new_status, old_ticket['status'], ticket_id, 0)

        # automatically set new priority
        perform_manual_priority_change(get_attribute_from_simular_tickets(sim_ticket_ids, "priority",
                                                                          old_ticket['priority']),
                                       old_ticket['priority'], ticket_id, 0)

        # automatically set new category
        new_category = get_attribute_from_simular_tickets(sim_ticket_ids, "category", None)
        perform_manual_category_change(new_category, old_ticket['category'], get_name_of_category(new_category)['name'],
                                       ticket_id, 0)

        # find solutions and proposed solutions in sim set
        potential_solutions = get_all_solutions_from_tickets(sim_ticket_ids)

        known_solutions = list(filter(lambda potential_solution:
                                      potential_solution['action_type'] in (PROVIDED_RESOLUTION_ACTION,
                                                                            PROPOSED_A_SOLUTION_ACTION),
                                      potential_solutions))

        if len(known_solutions) < 1:
            known_solutions = potential_solutions

        # propose solutions found from other tickets
        if len(known_solutions) > 1:
            for solution in known_solutions:
                if len(check_ticket_already_has_proposed_solution(solution['action_content'], ticket_id)) < 1:
                    insert_action_into_db(ticket_id, PROPOSED_A_SOLUTION_ACTION, solution['action_content'], 0)
            perform_manual_status_change(DB_TICKET_STATUS_VALUE[3], old_ticket['status'], ticket_id, 0)

    return ticket_sims


def get_attribute_from_simular_tickets(sim_ticket_ids, field, default):
    """ find common field value from ticket group """

    db = get_db()
    common_field_value = db.execute(f"SELECT {field} FROM ticket Where id IN ({sim_ticket_ids})"
                                    f" GROUP BY {field}").fetchall()

    if len(common_field_value) == 1:
        return common_field_value[0][field]
    else:
        return default


def perform_ticket_analysis(apply_actions, ticket_id):
    """ initiate ticket similarity analysis """

    similar_tickets = get_sorted_ticket_sim_analysis_results(ticket_id)

    if not (apply_actions is None or apply_actions is False):
        similar_tickets = apply_actions_from_ticket_sim_analysis(similar_tickets, ticket_id)

    delete_ticket_similarities_for_ticket(ticket_id)
    for ticket_sim in similar_tickets:
        insert_ticket_similarity(ticket_id, ticket_sim[0], round(ticket_sim[1], 4), round(ticket_sim[2], 4))
