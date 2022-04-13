""" views for landing page """

from flask import (
    Blueprint, render_template
)

from core_platform.utils.constants import INDEX_PAGE_TEMPLATE_LOCATION

bp = Blueprint('dashboards', __name__)


@bp.route('/')
def index():
    """ view for route directory to display the user's ticket dashboard """
    return render_template(INDEX_PAGE_TEMPLATE_LOCATION)
