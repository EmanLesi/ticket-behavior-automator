import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the core platform
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'core_platform_db.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialise database instance
    from core_platform.db import db_manager
    db_manager.init_app(app)

    # linking views for user authorisation
    from core_platform.auth import user_auth
    app.register_blueprint(user_auth.bp)

    # linking views for dashboard
    from core_platform.views import dashboard
    app.register_blueprint(dashboard.bp)
    app.add_url_rule('/', endpoint='index')

    # linking views for tickets
    from core_platform.views import tickets
    app.register_blueprint(tickets.bp)

    # a simple page that confirms that the service is online
    @app.route('/healthcheck')
    def healthcheck():
        return {"Server Status": "online"}

    return app
