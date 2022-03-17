""" views for ticket management dashboard """

from flask import (
    Blueprint, render_template
)

bp = Blueprint('dashboards', __name__)


@bp.route('/')
def index():
    """ view for route directory to display the user's ticket dashboard """
    return render_template('dashboards/index.html')
