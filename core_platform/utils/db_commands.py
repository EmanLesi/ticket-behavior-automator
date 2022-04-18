""" reoccurring database interactions """
from core_platform.db.db_manager import get_db
from core_platform.utils.constants import DB_CATEGORY_NONE_NAME, DB_TICKET_STATUS_VALUE, DB_TICKET_PRIORITY_VALUE, \
    DB_FAIL, DB_SUCCESS, DB_TICKET_FIELD_NAMES


def fetchall_tickets_for_index():
    """ retrieve all tickets and associated values from other tables in db """

    return get_db().execute('SELECT ticket.id, title, user_reporter.username as user_reporter_name, '
                            'user_assignee.username as user_assignee_name, description, category as category_id, '
                            'ticket.creation_time, update_time, priority, status, category.name as category_name'
                            ' FROM ticket ticket LEFT JOIN user user_reporter ON ticket.reporter = user_reporter.id'
                            ' LEFT JOIN user user_assignee ON ticket.assignee = user_assignee.id'
                            ' LEFT JOIN category category ON ticket.category = category.id'
                            ' ORDER BY ticket.creation_time DESC').fetchall()


def query_tickets_for_index(query_field=None, query_value=None, order_field='creation_time', order_value='DESC'):
    """ retrieve tickets that fit the criteria and in the specified order """

    if query_field is None or query_value is None:
        text_filter = ''
    else:
        text_filter = f" WHERE {query_field} LIKE '%{query_value}%'"

    if query_field == DB_TICKET_FIELD_NAMES[3] and query_value == 'None':
        text_filter = " WHERE category IS NULL"

    return get_db().execute('SELECT ticket.id, title, user_reporter.username as user_reporter_name, '
                            'user_assignee.username as user_assignee_name, description, category as category_id, '
                            'ticket.creation_time, update_time, priority, status, category.name as category_name'
                            ' FROM ticket ticket LEFT JOIN user user_reporter ON ticket.reporter = user_reporter.id'
                            ' LEFT JOIN user user_assignee ON ticket.assignee = user_assignee.id'
                            ' LEFT JOIN category category ON ticket.category = category.id'
                            f'{text_filter} ORDER BY ticket.{order_field} {order_value}').fetchall()


def get_individual_ticket_for_edit(ticket_id):
    """ retrieve a specific ticket from db """

    return get_db().execute('SELECT status, priority, category, assignee FROM ticket WHERE id = ?',
                            (ticket_id,)).fetchone()


def get_individual_ticket_for_view(ticket_id):
    """ retrieve specific tickets and associated values from other tables in db """

    return get_db().execute(
        'SELECT ticket.id, title, user_reporter.username as user_reporter_name, short_description_flag,'
        ' user_assignee.username as user_assignee_name, description, category as category_id, '
        'ticket.creation_time, update_time, priority, status, category.name as category_name'
        ' FROM ticket ticket LEFT JOIN user user_reporter ON ticket.reporter = user_reporter.id'
        ' LEFT JOIN user user_assignee ON ticket.assignee = user_assignee.id'
        ' LEFT JOIN category category ON ticket.category = category.id'
        ' WHERE ticket.id = ?', (ticket_id,)).fetchone()


def get_individual_ticket_for_sim_analysis(ticket_id):
    """ get ticket fields for individual ticket that is required for NLP analysis """

    return get_db().execute("SELECT id, title, description, short_description_flag FROM ticket WHERE id = ?",
                            (ticket_id,)).fetchone()


def get_ticket_actions_for_view(ticket_id):
    """ retrieve all actions performed on ticket """

    return get_db().execute('SELECT creation_time, action_type, action_content, ticket_action.id as action_id, '
                            'user.username as username, ticket_action.associated_user as associated_user_id '
                            'FROM ticket_action ticket_action '
                            'LEFT JOIN user user ON associated_user = user.id '
                            'WHERE ticket = ? '
                            'ORDER BY creation_time DESC', (ticket_id,)).fetchall()


def get_all_other_ticket_titles_and_descriptions(ticket_id):
    """ get the titles and descriptions of other tickets  """

    return get_db().execute("SELECT id, title, description FROM ticket WHERE id != ?", (ticket_id,)).fetchall()


def get_ticket_reporter(ticket_id):
    """ get the reporter id of a specific ticket """

    return get_db().execute("SELECT reporter FROM ticket WHERE id = ?", (ticket_id,)).fetchone()


def get_most_recent_solution(ticket_id):
    """ get the most recent solution to a ticket """

    return get_db().execute("SELECT id FROM ticket_action WHERE ticket = ? AND"
                            "(action_type = 'PROPOSED A SOLUTION' OR action_type = 'PROVIDED RESOLUTION') "
                            "ORDER BY creation_time DESC", (ticket_id,)).fetchone()


def get_all_solutions_from_tickets(ticket_ids):
    """ get all proposed solutions from a group of tickets """

    return get_db().execute("SELECT ta.ticket, ta.action_type as action_type, ta.action_content as action_content "
                            "FROM ticket_action ta LEFT JOIN ticket_similarity ts ON ta.ticket = ts.comp_ticket "
                            f"WHERE ta.ticket IN ({ticket_ids}) and (ta.action_type = 'PROVIDED RESOLUTION' "
                            "OR ta.action_type = 'PROPOSED A SOLUTION') "
                            "ORDER BY (ts.title_sim + ts.desc_sim)").fetchall()


def get_unresolved_similar_tickets_ids(ticket_id):
    """ get ids similar unresolved tickets to a ticket """

    db = get_db()
    ticket_sims_from_comp_ticket = db.execute("SELECT ts.ticket as id FROM ticket_similarity ts LEFT JOIN ticket ticket"
                                              " ON ts.ticket = ticket.id WHERE ts.comp_ticket = ? "
                                              "AND ticket.status != 'closed'", (ticket_id,)).fetchall()

    ticket_sims_from_ticket = db.execute("SELECT ts.comp_ticket as id FROM ticket_similarity ts LEFT JOIN ticket ticket"
                                         " ON ts.comp_ticket = ticket.id WHERE ts.ticket = ?"
                                         " AND ticket.status != 'closed'", (ticket_id,)).fetchall()

    return ticket_sims_from_comp_ticket + ticket_sims_from_ticket


def get_ticket_id(ticket_id):
    """ varify that a ticket exist in database """

    return get_db().execute("SELECT id FROM ticket WHERE id = ?", (ticket_id,)).fetchone()


def get_ticket_similarities_for_view(ticket_id):
    """ get the similar tickets for specific ticket """

    return get_db().execute('SELECT comp_ticket, title_sim, desc_sim FROM ticket_similarity'
                            ' WHERE ticket = ? ', (ticket_id,)).fetchall()


def get_all_registered_users():
    """ retrieve all usernames in db """

    return get_db().execute('SELECT username FROM user').fetchall()


def get_all_category_names():
    """ retrieve all category names in db """

    return get_db().execute('SELECT name FROM category').fetchall()


def get_username_from_id(user_id):
    """ get username from id """

    return get_db().execute('SELECT username from user WHERE id = ?', (user_id,)).fetchone()


def get_id_of_user(username):
    """ get id from username """

    return get_db().execute('SELECT id from user WHERE username = ?', (username,)).fetchone()


def get_id_of_category(category_name):
    """ get id from category name """

    if category_name == DB_CATEGORY_NONE_NAME:
        return {'id': None}

    return get_db().execute('SELECT id FROM category WHERE name = ?', (category_name,)).fetchone()


def get_name_of_category(category_id):
    """ get name from category id """

    category_name = get_db().execute('SELECT name FROM category WHERE id = ?', (category_id,)).fetchone()
    if category_name is None:
        category_name = {'name': DB_CATEGORY_NONE_NAME}
    return category_name


def get_id_of_the_newest_ticket():
    """ get the id of the last ticket that was created in the db """

    return get_db().execute("SELECT MAX(id) as id FROM ticket").fetchone()


def insert_new_ticket_into_db(title, description, reporter, short_description_flag):
    """ insert new ticket in to db """

    db = get_db()
    try:
        db.execute('INSERT INTO ticket (title, description, reporter, status, priority, short_description_flag)'
                   ' VALUES (?,?,?,?,?,?)',
                   (title, description, reporter, DB_TICKET_STATUS_VALUE[0], DB_TICKET_PRIORITY_VALUE[0],
                    short_description_flag))
        db.commit()
    except db.Error:
        return DB_FAIL
    return DB_SUCCESS


def insert_action_into_db(ticket_id, action_type, action_content, user_id):
    """ record actions being performed on tickets """

    db = get_db()
    try:
        db.execute('INSERT INTO ticket_action (ticket, action_type, action_content, associated_user) '
                   'VALUES (?,?,?,?)',
                   (ticket_id, action_type, action_content, user_id))
        db.commit()
    except db.Error:
        return DB_FAIL
    return DB_SUCCESS


def get_ticket_action_by_id(action_id):
    """ retrieve action by id """

    return get_db().execute("SELECT action_type, action_content FROM ticket_action "
                            "WHERE id = ?", (action_id,)).fetchone()


def check_ticket_already_has_proposed_solution(action_content, ticket_id):
    """ find proposed solutions on a ticket based on its action content  """

    return get_db().execute("SELECT id FROM ticket_action WHERE (action_type = 'PROPOSED A SOLUTION' OR"
                            " action_type = 'PROVIDED RESOLUTION') AND ticket = ? AND action_content = ?",
                            (ticket_id, action_content,)).fetchall()


def set_ticket_update_time_to_now(ticket_id):
    """ set the last update time of a ticket to the current date and time """

    db = get_db()
    db.execute("UPDATE ticket SET update_time = datetime('now') WHERE id = ? ", (ticket_id,))
    db.commit()


def set_ticket_status_in_db(status, ticket_id):
    """ set ticket status in db """

    db = get_db()
    db.execute("UPDATE ticket SET status = ? WHERE id = ?", (status, ticket_id,))
    db.commit()


def set_ticket_priority_in_db(priority, ticket_id):
    """ set ticket priority in db """

    db = get_db()
    db.execute("UPDATE ticket SET priority = ? WHERE id = ?", (priority, ticket_id,))
    db.commit()


def set_ticket_category_in_db(category, ticket_id):
    """ set ticket category in db """

    db = get_db()
    db.execute("UPDATE ticket SET category = ? WHERE id = ?", (category, ticket_id,))
    db.commit()


def set_ticket_assignee_in_db(assignee, ticket_id):
    """ set ticket assignee in db """

    db = get_db()
    db.execute("UPDATE ticket SET assignee = ? WHERE id = ?", (assignee, ticket_id,))
    db.commit()


def insert_new_category(category_name):
    """ insert new category into db """

    db = get_db()
    db.execute('INSERT INTO category (name) VALUES (?)', (category_name,))
    db.commit()


def change_action_type_on_ticket_action(action_type, action_id):
    """ change action type on ticket action """

    db = get_db()
    db.execute("UPDATE ticket_action SET action_type = ? WHERE id = ?", (action_type, action_id,))
    db.commit()


def delete_action_from_ticket(ticket_id, action_id):
    """ delete action from ticket actions """

    db = get_db()
    db.execute('DELETE FROM ticket_action WHERE ticket = ? AND id = ?', (ticket_id, action_id,))
    db.commit()


def delete_all_associated_with_ticket(ticket_id):
    """ delete every data point associated with a ticket """

    db = get_db()
    db.execute('DELETE FROM ticket_action WHERE ticket = ?', (ticket_id,))
    db.execute('DELETE FROM ticket WHERE id = ?', (ticket_id,))
    db.execute('DELETE FROM ticket_similarity WHERE ticket = ? OR comp_ticket = ?', (ticket_id, ticket_id,))
    db.commit()


def delete_ticket_similarities_for_ticket(ticket_id):
    """ delete similarities for ticket """

    db = get_db()
    db.execute('DELETE FROM ticket_similarity WHERE ticket = ?', (ticket_id,))
    db.commit()


def insert_ticket_similarity(ticket_id, comp_ticket, title_sim, desc_sim):
    """ add ticket similarity value to db """

    db = get_db()
    db.execute("INSERT INTO ticket_similarity (ticket, comp_ticket, title_sim, desc_sim) "
               "VALUES (?,?,?,?)", (ticket_id, comp_ticket, title_sim, desc_sim))
    db.commit()
