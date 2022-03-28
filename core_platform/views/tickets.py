from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from core_platform.auth.user_auth import login_required
from core_platform.db.db_manager import get_db

bp = Blueprint('ticket_views', __name__, url_prefix='/ticket')


@bp.route("/")
def ticket_index():
    """ view all tickets """

    db = get_db()
    tickets = db.execute('SELECT ticket.id, title, user_reporter.username as user_reporter_name, '
                         'user_assignee.username as user_assignee_name, description, category as category_id, '
                         'ticket.creation_time, update_time, priority, status, category.name as category_name'
                         ' FROM ticket ticket LEFT JOIN user user_reporter ON ticket.reporter = user_reporter.id'
                         ' LEFT JOIN user user_assignee ON ticket.assignee = user_assignee.id'
                         ' LEFT JOIN category category ON ticket.category = category.id'
                         ' ORDER BY ticket.creation_time DESC').fetchall()
    return render_template('dashboards/ticket_index.html', tickets=tickets)


@bp.route('/create_ticket', methods=('GET', 'POST'))
@login_required
def create_ticket():
    """ create a new ticket in the db """

    if request.method == 'POST':
        error = None
        title = request.form['title']
        description = request.form['description']

        # perform presence check for title
        if title is None or title.isspace() or len(title) < 1:
            error = 'Title is required.'

        # insert new ticket into db with initial values for status and priority
        if error is None:
            db = get_db()
            try:
                db.execute('INSERT INTO ticket (title, description, reporter, status, priority) '
                           'VALUES (?,?,?,?,?)',
                           (title, description, g.user['id'], "new", "none"))
                db.commit()
                return redirect(url_for('ticket_views.ticket_index'))

            except db.Error:
                error = f"Unable To Create Ticket - Invalid Content"

        flash(error)

    return render_template('dashboards/create_ticket.html')


def is_valid_text_field(field_value):
    """ input validation for text fields """

    if field_value is None or field_value.isspace() or len(field_value) < 1:
        return False
    return True


def is_valid_drop_down_field(field_value, field_name):
    """ input validation for dropdown  fields """

    if field_value is None or field_value == f"select new {field_name}":
        return False
    return True


def perform_action_on_ticket(db, ticket_id, action_type, action_content, user_id):
    """ record actions being performed on tickets """

    db.execute('INSERT INTO ticket_action (ticket, action_type, action_content, associated_user) '
               'VALUES (?,?,?,?)',
               (ticket_id, action_type, action_content, user_id))
    return


@bp.route('make_comment/<int:ticket_id>/', methods=('POST',))
@login_required
def make_comment_on_ticket(ticket_id):
    """ add a comment to the actions performed on a ticket """

    if request.method == 'POST':
        comment_action = request.form['comment_action']
        solution_checkbox = request.form.get('solution_checkbox')

        # varify that comment has content
        if is_valid_text_field(comment_action):
            db = get_db()

            comment_type = "MADE A COMMENT"

            # check if comment is a solution
            if solution_checkbox is not None and solution_checkbox == 'True':
                comment_type = "PROPOSED A SOLUTION"
                db.execute("UPDATE ticket SET status = 'solution proposed' WHERE id = ?",
                           (ticket_id,)).fetchone()
                db.commit()

            # add comment to action on a ticket
            try:
                user_id = db.execute('SELECT id from user WHERE username = ?', (g.user['username'],)).fetchone()['id']
                perform_action_on_ticket(db, ticket_id, comment_type, comment_action, user_id)
                db.commit()
            except db.Error:
                flash("COMMENT NOT ADDED - unable to add comment to ticket")
        else:
            flash("COMMENT NOT ADDED - your comment does not have any content")
        return redirect(url_for('ticket_views.edit', ticket_id=ticket_id))


@login_required
@bp.route('/<int:ticket_id>/edit', methods=('POST', 'GET'))
def edit(ticket_id):
    """
    GET: display ticket attributes
    POST: make changes to a ticket's attributes
    """

    if request.method == "POST":

        db = get_db()
        # extract form data
        new_category_name = request.form['category']
        new_assignee_user = request.form['assignee']
        new_status = request.form['status']
        new_priority = request.form['priority']

        # fetch existing ticket data
        old_ticket = db.execute('SELECT status, priority, category, assignee FROM ticket WHERE id = ?',
                                (ticket_id,)).fetchone()

        old_status = old_ticket['status']
        old_priority = old_ticket['priority']
        old_assignee = old_ticket['assignee']
        old_category = old_ticket['category']

        user_id = db.execute('SELECT id from user WHERE username = ?', (g.user['username'],)).fetchone()['id']

        # set new status
        if is_valid_drop_down_field(new_status, "status") and new_status != old_status:
            perform_action_on_ticket(db, ticket_id, "CHANGED STATUS", new_status, user_id)
            db.execute('UPDATE ticket SET status = ? WHERE id = ?', (new_status, ticket_id))

        # set new priority
        if is_valid_drop_down_field(new_priority, "priority") and new_priority != old_priority:
            perform_action_on_ticket(db, ticket_id, "CHANGED PRIORITY", new_priority, user_id)
            db.execute('UPDATE ticket SET priority = ? WHERE id = ?', (new_priority, ticket_id))

        if is_valid_text_field(new_category_name):
            # check if new category already exists
            new_category = db.execute('SELECT id FROM category WHERE name = ?', (new_category_name,)).fetchone()

            # add new category of it does not currently exist
            if new_category is None:
                db.execute('INSERT INTO category (name) VALUES (?)', (new_category_name,))
                new_category = db.execute('SELECT id FROM category WHERE name = ?', (new_category_name,)).fetchone()

            if new_category['id'] != old_category:
                perform_action_on_ticket(db, ticket_id, "CHANGED CATEGORY", new_category_name, user_id)
                db.execute('UPDATE ticket SET category = ? WHERE id = ?', (new_category['id'], ticket_id))

        if is_valid_text_field(new_assignee_user):
            # varify the existence of the assignee as a user in the system
            new_assignee = db.execute('SELECT id FROM user WHERE username = ?', (new_assignee_user,)).fetchone()

            # set new assignee
            if new_assignee is not None:
                new_assignee_id = new_assignee['id']
                if new_assignee_id != old_assignee:
                    perform_action_on_ticket(db, ticket_id, "CHANGED ASSIGNEE", new_assignee_user, user_id)
                    db.execute('UPDATE ticket SET assignee = ? WHERE id = ?', (new_assignee_id, ticket_id))
                    db.execute("UPDATE ticket SET status = 'assigned' WHERE id = ?",
                               (ticket_id,)).fetchone()
            else:
                flash("NEW ASSIGNEE USER NOT FOUND - restoring previous value")

        db.commit()

    db = get_db()
    # get all associated ticket data across tables in the database
    ticket = db.execute('SELECT ticket.id, title, user_reporter.username as user_reporter_name, '
                        'user_assignee.username as user_assignee_name, description, category as category_id, '
                        'ticket.creation_time, update_time, priority, status, category.name as category_name'
                        ' FROM ticket ticket LEFT JOIN user user_reporter ON ticket.reporter = user_reporter.id'
                        ' LEFT JOIN user user_assignee ON ticket.assignee = user_assignee.id'
                        ' LEFT JOIN category category ON ticket.category = category.id'
                        ' WHERE ticket.id = ?', (ticket_id,)).fetchone()

    # return 404 if ticket is not found
    if ticket is None:
        abort(404, f"Ticket with id {ticket_id} does not exist.")

    # get assignee, category and actions that have been preformed on the ticket
    ticket_actions = db.execute('SELECT creation_time, action_type, action_content, ticket_action.id as action_id, '
                                'user.username as username '
                                'FROM ticket_action ticket_action '
                                'LEFT JOIN user user ON associated_user = user.id '
                                'WHERE ticket = ? '
                                'ORDER BY creation_time DESC', (ticket_id,)).fetchall()

    assignees = db.execute('SELECT username FROM user').fetchall()
    registered_categories = db.execute('SELECT DISTINCT name FROM category').fetchall()

    return render_template('dashboards/ticket_details.html', ticket=ticket, ticket_actions=ticket_actions,
                           available_assignee=assignees, registered_categories=registered_categories)


@login_required
@bp.route('/<int:ticket_id>/solution_feedback', methods=('POST',))
def solution_feedback(ticket_id):
    """ record feedback from the reporter on the most recent solution """

    if request.method == "POST":
        # extract feedback value
        feedback = request.form.get('solution_feedback')

        db = get_db()

        # confirm session user as reporter
        ticket = db.execute("SELECT reporter FROM ticket WHERE id = ?", (ticket_id,)).fetchone()

        if feedback is not None and ticket['reporter'] == g.user['id']:

            last_solution = db.execute("SELECT id FROM ticket_action WHERE ticket = ? AND"
                                       "(action_type = 'PROPOSED A SOLUTION' OR action_type = 'PROVIDED RESOLUTION') "
                                       "ORDER BY creation_time DESC", (ticket_id,)).fetchone()

            # perform appropriate feedback procedures
            if last_solution is not None:
                content, solution_status, new_ticket_status = None, None, None
                if feedback == "resolved by proposed solution":
                    content, solution_status, new_ticket_status = "confirmed solution", 'PROVIDED RESOLUTION', 'closed'

                elif feedback == "proposed solution was not affective":
                    content, solution_status, new_ticket_status = "rejected solution",\
                                                                  'PROPOSED A SOLUTION', 'solution ineffective'

                if content is not None and solution_status is not None and new_ticket_status is not None:
                    perform_action_on_ticket(db, ticket_id, "PROVIDED FEEDBACK", content, g.user['id'])
                    db.execute("UPDATE ticket_action SET action_type = ? WHERE id = ?",
                               (solution_status, last_solution['id'],)).fetchone()
                    db.execute("UPDATE ticket SET status = ? WHERE id = ?",
                               (new_ticket_status, ticket_id,)).fetchone()

            else:
                flash("no solutions have been proposed - enter a solution comment then provide feedback")
        db.commit()

    return redirect(url_for('ticket_views.edit', ticket_id=ticket_id))


@login_required
@bp.route('/<int:ticket_id>/delete_action/<int:action_id>', methods=('POST',))
def delete_action(ticket_id, action_id):
    """ delete an action from a ticket's history """

    db = get_db()
    ticket = db.execute("SELECT id FROM ticket WHERE id = ?", (ticket_id,)).fetchone()
    if ticket is not None:
        db.execute('DELETE FROM ticket_action WHERE ticket = ? AND id = ?', (ticket_id, action_id,))
        db.commit()
        return redirect(url_for('ticket_views.edit', ticket_id=ticket_id))
    flash('ticket is associated with action - returning to ticket index')
    return redirect(url_for('ticket_views.ticket_index'))


@login_required
@bp.route('/<int:ticket_id>/delete', methods=('POST',))
def delete_ticket(ticket_id):
    """ delete a ticket and related objects"""

    db = get_db()
    db.execute('DELETE FROM ticket_action WHERE ticket = ?', (ticket_id,))
    db.execute('DELETE FROM ticket WHERE id = ?', (ticket_id,))
    db.commit()
    return redirect(url_for('ticket_views.ticket_index'))
