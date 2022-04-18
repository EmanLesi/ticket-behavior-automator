""" constant values used throughout the core platform """
import spacy

# file locations
INDEX_PAGE_TEMPLATE_LOCATION = "dashboards/index.html"
TICKET_INDEX_PAGE_TEMPLATE_LOCATION = "dashboards/ticket_index.html"
VIEW_TICKET_PAGE_TEMPLATE_LOCATION = "dashboards/ticket_details.html"
CREATE_TICKET_PAGE_TEMPLATE_LOCATION = "dashboards/create_ticket.html"
AUTH_REGISTER_PAGE_TEMPLATE = "auth/register.html"
AUTH_LOGIN_PAGE_TEMPLATE = "auth/login.html"


# redirects
AUTH_LOGIN_VIEW = 'auth.login'
TICKET_INDEX_VIEW = 'ticket_views.ticket_index'
VIEW_TICKET_VIEW = 'ticket_views.edit'
INDEX_VIEW = 'index'


# database constants
DB_SUCCESS = "DB COMMIT WAS SUCCESSFUL"
DB_FAIL = "DB COMMIT FAILED"
DB_TICKET_FIELD_NAMES = ["id", "title", "description", "category", "status", "reporter", "assignee", "priority",
                         "short_description_flag", "creation_time", "update_time"]
DB_TICKET_STATUS_VALUE = ["new", "assigned", "under investigation", "solution proposed", "solution ineffective",
                          "closed"]
DB_TICKET_PRIORITY_VALUE = ["none", "low", "medium", "high", "critical"]
DB_CATEGORY_NONE_NAME = "None"
TEXT_INPUT_CHARACTER_LIMIT = 512
DB_FIELD_ORDER_ASC = "ASC"
DB_FIELD_ORDER_DESC = "DESC"


# error messages
TITLE_IS_REQUIRED = "Title is required"
UNABLE_TO_CREATE_TICKET_INVALID_CONTENT = "Unable To Create Ticket - Invalid Content"
COMMENT_NOT_ADDED_DB_ISSUE = "COMMENT NOT ADDED - unable to add comment to ticket"
COMMENT_NOT_ADDED_NO_CONTENT = "COMMENT NOT ADDED - your comment does not have any content"
NEW_ASSIGNEE_NOT_FOUND = "NEW ASSIGNEE USER NOT FOUND - restoring previous value"
NOT_A_USER = "{} - Is not a registered user"
NOT_A_CATEGORY = "{} - Is not a registered category"
TICKET_NOT_FOUND = "Ticket with id {} does not exist."
NO_SOLUTIONS_HAVE_BEEN_PROPOSED = "no solutions have been proposed - enter a solution comment then provide feedback"
SELECT_FEEDBACK_OPTION = "Please select a feedback option"
DESCRIPTION_LENGTH_ABOVE_CHARACTER_LIMIT = f"the description is longer than the limit of {TEXT_INPUT_CHARACTER_LIMIT}" \
                                           f" characters"


# nlp constants
SPACY_PIPELINE = 'en_core_web_lg'
NLP = spacy.load(SPACY_PIPELINE)
DEFAULT_FOR_NO_DESCRIPTION = "NO DESCRIPTION"
TITLE_SIMILARITY_THRESHOLD = 0.8
TITLE_WITH_DESC_SIMILARITY_THRESHOLD = 1.6
SIMILARITY_GROUP_SIZE = 3
DEFAULT_APPLY_ACTIONS_ON_CREATE = True


# ticket action types
MADE_A_COMMENT_ACTION = "MADE A COMMENT"
PROPOSED_A_SOLUTION_ACTION = "PROPOSED A SOLUTION"
CHANGED_STATUS_ACTION = "CHANGED STATUS"
CHANGED_PRIORITY_ACTION = "CHANGED PRIORITY"
CHANGED_CATEGORY_ACTION = "CHANGED CATEGORY"
CHANGED_ASSIGNEE_ACTION = "CHANGED ASSIGNEE"
PROVIDED_RESOLUTION_ACTION = "PROVIDED RESOLUTION"
PROVIDED_FEEDBACK_ACTION = "PROVIDED FEEDBACK"


# feedback types
RESOLVED_BY_PROPOSED_SOLUTION = "resolved by proposed solution"
CONFIRMED_SOLUTION = "confirmed solution"
PROPOSED_SOLUTION_INEFFECTIVE = "proposed solution was not effective"
REJECTED_SOLUTION = "rejected solution"

PROPAGATE_SOLUTIONS = True
