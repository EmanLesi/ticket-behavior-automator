""" views for ticket management  """

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from core_platform.auth.user_auth import login_required
from core_platform.nlp.ticket_analysis import perform_ticket_analysis
from core_platform.utils.procedures import *

bp = Blueprint('ticket_views', __name__, url_prefix='/ticket')


@bp.route("/")
def ticket_index():
    """ view all tickets """

    existing_categories = get_all_category_names()

    return render_template(TICKET_INDEX_PAGE_TEMPLATE_LOCATION, existing_categories_length=len(existing_categories),
                           existing_categories=existing_categories, tickets=fetchall_tickets_for_index())


@bp.route('/create_ticket', methods=('GET', 'POST'))
@login_required
def create_ticket():
    """ create a new ticket in the db """

    if request.method == 'POST':
        error = None
        title = request.form.get('title')
        description = request.form.get('description')

        # perform presence check for title
        if not (is_valid_text_field(title)):
            error = TITLE_IS_REQUIRED

        # insert new ticket into db with initial values for status and priority
        if error is None:
            if len(description) < TEXT_INPUT_CHARACTER_LIMIT:

                # perform complexity check for description
                short_description_flag = 1
                if len(clean_text_of_stop_words(description)) > 30:
                    short_description_flag = 0

                if insert_new_ticket_into_db(title, description, g.user['id'], short_description_flag) == DB_SUCCESS:
                    perform_ticket_analysis(DEFAULT_APPLY_ACTIONS_ON_CREATE, get_id_of_the_newest_ticket()['id'])
                    return redirect(url_for(TICKET_INDEX_VIEW))
                else:
                    error = UNABLE_TO_CREATE_TICKET_INVALID_CONTENT
            else:
                error = DESCRIPTION_LENGTH_ABOVE_CHARACTER_LIMIT

        flash(error)

    return render_template(CREATE_TICKET_PAGE_TEMPLATE_LOCATION)


@bp.route('make_comment/<int:ticket_id>/', methods=('POST',))
@login_required
def make_comment_on_ticket(ticket_id):
    """ add a comment to the actions performed on a ticket """

    if request.method == 'POST':
        comment_action = request.form.get('comment_action')
        solution_checkbox = request.form.get('solution_checkbox')

        # varify that comment has content
        if is_valid_text_field(comment_action):

            comment_type = MADE_A_COMMENT_ACTION

            # check if comment is a solution
            if get_check_box_value(solution_checkbox):
                comment_type = PROPOSED_A_SOLUTION_ACTION

            # add comment to action on a ticket
            user_id = get_id_of_user(g.user['username'])['id']
            if insert_action_into_db(ticket_id, comment_type, comment_action, user_id) == DB_FAIL:
                flash(COMMENT_NOT_ADDED_DB_ISSUE)
            else:
                if comment_type == PROPOSED_A_SOLUTION_ACTION:
                    set_ticket_status_in_db(DB_TICKET_STATUS_VALUE[3], ticket_id)
                set_ticket_update_time_to_now(ticket_id)
                flash(COMMENT_MADE.format(g.user['username'], comment_type.lower()))
        else:
            flash(COMMENT_NOT_ADDED_NO_CONTENT)
        return redirect(url_for(VIEW_TICKET_VIEW, ticket_id=ticket_id))


@login_required
@bp.route('/<int:ticket_id>/edit', methods=('POST', 'GET'))
def edit(ticket_id):
    """
    GET: display ticket attributes
    POST: make changes to a ticket's attributes
    """

    if request.method == "POST":

        # extract form data
        new_category_name = request.form['category']
        new_assignee_user = request.form['assignee']
        new_status = request.form['status']
        new_priority = request.form['priority']

        # fetch existing ticket data
        old_ticket = get_individual_ticket_for_edit(ticket_id)

        old_status = old_ticket['status']
        old_priority = old_ticket['priority']
        old_assignee = old_ticket['assignee']
        old_category = old_ticket['category']

        user_id = get_id_of_user(g.user['username'])['id']

        # set new category
        if is_valid_text_field(new_category_name):

            new_category_name = new_category_name.title()

            # check if new category already exists
            new_category = get_id_of_category(new_category_name)

            # add new category of it does not currently exist
            if new_category is None and new_category_name != DB_CATEGORY_NONE_NAME:
                insert_new_category(new_category_name)
                new_category = get_id_of_category(new_category_name)

            if perform_manual_category_change(new_category['id'], old_category, new_category_name, ticket_id, user_id):
                flash(FIELD_UPDATE_SUCCESS.format(DB_TICKET_FIELD_NAMES[3], get_name_of_category(old_category)['name'],
                                                  new_category_name))

        elif len(new_category_name) > TEXT_INPUT_CHARACTER_LIMIT:
            flash(NEW_CATEGORY_NAME_IS_TOO_LONG)

        # set new assignee
        if is_valid_text_field(new_assignee_user):
            # varify the existence of the assignee as a user in the system
            new_assignee = get_id_of_user(new_assignee_user)

            # set new assignee
            if new_assignee is not None:
                if perform_manual_assignee_change(new_assignee['id'], old_assignee, new_assignee_user, ticket_id,
                                                  user_id):
                    flash(FIELD_UPDATE_SUCCESS.format(DB_TICKET_FIELD_NAMES[6],
                                                      get_username_from_id(old_assignee)['username'],
                                                      new_assignee_user))

            else:
                flash(NEW_ASSIGNEE_NOT_FOUND)

        # set new status
        if perform_manual_status_change(new_status, old_status, ticket_id, user_id):
            flash(FIELD_UPDATE_SUCCESS.format(DB_TICKET_FIELD_NAMES[4], old_status, new_status))

        # set new priority
        if perform_manual_priority_change(new_priority, old_priority, ticket_id, user_id):
            flash(FIELD_UPDATE_SUCCESS.format(DB_TICKET_FIELD_NAMES[7], old_priority, new_priority))

    # get all associated ticket data across tables in the database
    ticket = get_individual_ticket_for_view(ticket_id)

    # return 404 if ticket is not found
    if ticket is None:
        abort(404, TICKET_NOT_FOUND.format(ticket_id))

    # get assignee, category and actions that have been preformed on the ticket
    ticket_actions = get_ticket_actions_for_view(ticket_id)

    # get ticket similarities
    ticket_sims = get_ticket_similarities_for_view(ticket_id)

    similar_ticket_attributes = {}

    for similar_ticket in ticket_sims:
        similar_ticket_fields = get_individual_ticket_for_edit(similar_ticket['comp_ticket'])
        similar_ticket_attributes[similar_ticket['comp_ticket']] = [similar_ticket_fields['status'],
                                                                    similar_ticket_fields['priority'],
                                                                    get_username_from_id(
                                                                        similar_ticket_fields['assignee'])['username'],
                                                                    get_name_of_category(
                                                                        similar_ticket_fields['category'])['name'],
                                                                    len(get_all_solutions_from_tickets(
                                                                        similar_ticket['comp_ticket']))]

    # resolve recommendations for view
    recommended_values = None

    if len(similar_ticket_attributes) > 0:
        recommended_values = extract_recommended_values(list(similar_ticket_attributes.values()))

    # get existing users and categories
    assignees = get_all_registered_users()
    registered_categories = get_all_category_names()

    return render_template(VIEW_TICKET_PAGE_TEMPLATE_LOCATION, ticket=ticket, ticket_actions=ticket_actions,
                           available_assignees=assignees, registered_categories=registered_categories,
                           ticket_sims=ticket_sims, similar_ticket_attributes=similar_ticket_attributes,
                           recommended_values=recommended_values)


@login_required
@bp.route('/<int:ticket_id>/solution_feedback', methods=('POST',))
def solution_feedback(ticket_id):
    """ record feedback from the reporter on the most recent solution """

    if request.method == "POST":
        # extract feedback value
        feedback = request.form.get('solution_feedback')

        # confirm session user as reporter
        ticket = get_ticket_reporter(ticket_id)

        if feedback is not None and ticket['reporter'] == g.user['id']:

            last_solution = get_most_recent_solution(ticket_id)

            # perform appropriate feedback procedures
            if last_solution is not None:
                content, solution_status, new_ticket_status = None, None, None
                if feedback == RESOLVED_BY_PROPOSED_SOLUTION:
                    content, solution_status, new_ticket_status = CONFIRMED_SOLUTION, PROVIDED_RESOLUTION_ACTION, \
                                                                  DB_TICKET_STATUS_VALUE[5]

                elif feedback == PROPOSED_SOLUTION_INEFFECTIVE:
                    content, solution_status, new_ticket_status = REJECTED_SOLUTION, PROPOSED_A_SOLUTION_ACTION, \
                                                                  DB_TICKET_STATUS_VALUE[4]

                perform_solution_feedback(content, solution_status, new_ticket_status, last_solution['id'], ticket_id,
                                          g.user['id'])

                flash(SOLUTION_FEEDBACK_RECORDED.format(content))

            else:
                flash(NO_SOLUTIONS_HAVE_BEEN_PROPOSED)
        else:
            flash(SELECT_FEEDBACK_OPTION)

    return redirect(url_for(VIEW_TICKET_VIEW, ticket_id=ticket_id))


@login_required
@bp.route('/<int:ticket_id>/delete_action/<int:action_id>', methods=('POST',))
def delete_action(ticket_id, action_id):
    """ delete an action from a ticket's history """

    ticket = get_ticket_id(ticket_id)
    if ticket is not None:
        delete_action_from_ticket(ticket_id, action_id)
        flash(ACTION_DELETED)
        return redirect(url_for(VIEW_TICKET_VIEW, ticket_id=ticket_id))

    flash(TICKET_NOT_FOUND.format(ticket_id))
    return redirect(url_for(TICKET_INDEX_VIEW))


@login_required
@bp.route('/<int:ticket_id>/delete', methods=('POST',))
def delete_ticket(ticket_id):
    """ delete a ticket and related objects"""

    delete_all_associated_with_ticket(ticket_id)
    flash(TICKET_DELETED.format(ticket_id))
    return redirect(url_for(TICKET_INDEX_VIEW))


@login_required
@bp.route('/<int:ticket_id>/reassess_similarity', methods=('POST',))
def reassess_similarity(ticket_id):
    """ reassess ticket similarity """

    if request.method == "POST":
        apply_actions = request.args.get('apply_actions')

        if apply_actions == 'True':
            perform_ticket_analysis(True, ticket_id)
            flash(TICKET_SIMILARITY_UPDATE)
            flash(RECOMMEND_ACTIONS_APPLIED)
        else:
            perform_ticket_analysis(False, ticket_id)
            flash(TICKET_SIMILARITY_UPDATE)

    return redirect(url_for(VIEW_TICKET_VIEW, ticket_id=ticket_id))


@login_required
@bp.route('/query/', methods=('GET', 'POST',))
def query():
    """ view tickets that fit the user query """

    # extract values
    query_field = request.form.get("query_field")
    query_value = request.form.get("query_value")
    query_order_field = request.form.get("query_order_field")
    query_order_value = request.form.get("query_order_value")
    query_holding_value = None

    # validate and reform values
    if not is_valid_drop_down_field(query_field, DB_TICKET_FIELD_NAMES):
        query_field = None

    if not is_valid_text_field(query_value):
        query_value = None

    if query_field == DB_TICKET_FIELD_NAMES[3] and query_value is not None:
        query_value_category_record = get_id_of_category(query_value.title())
        if query_value_category_record is None:
            flash(NOT_A_CATEGORY.format(query_value))
            query_value = None
        else:
            query_value = query_value.title()
            query_holding_value = query_value
            if query_value != DB_CATEGORY_NONE_NAME:
                query_value = query_value_category_record['id']

    if (query_field == DB_TICKET_FIELD_NAMES[5] or query_field == DB_TICKET_FIELD_NAMES[6]) and query_value is not None:
        if query_value.title() == DB_USER_NONE_NAME:
            query_value = query_value.title()
            query_holding_value = query_value
        else:
            query_value_user_record = get_id_of_user(query_value)
            if query_value_user_record is None:
                flash(NOT_A_USER.format(query_value))
                query_value = None
            else:
                query_holding_value = query_value
                query_value = query_value_user_record['id']

    # validate query order
    if not ((is_valid_drop_down_field(query_order_field, DB_TICKET_FIELD_NAMES) and
             (query_order_value == DB_FIELD_ORDER_ASC or query_order_value == DB_FIELD_ORDER_DESC))):
        return redirect(url_for(TICKET_INDEX_VIEW))

    # return ticket index with tickets that fit the criteria
    existing_categories = get_all_category_names()
    return render_template(TICKET_INDEX_PAGE_TEMPLATE_LOCATION, existing_categories_length=len(existing_categories),
                           existing_categories=existing_categories,
                           tickets=query_tickets_for_index(query_field, query_value, query_order_field,
                                                           query_order_value),
                           query_field=query_field, query_value=query_value, query_order_field=query_order_field,
                           query_order_value=query_order_value, query_holding_value=query_holding_value)
