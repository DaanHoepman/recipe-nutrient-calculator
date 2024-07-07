import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.config import config_dict

#--------------------
lm = LoginManager()
db = SQLAlchemy()

def register_extensions(app):
    db.init_app(app)
    lm.init_app(app)

def register_blueprints(app):
    from .views.main_views import main
    from .views.auth_views import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    if app.config['DEBUG']:
        from .views.test_views import test
        app.register_blueprint(test)


def set_errorhandlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('home/page-404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('home/page-500.html'), 500
    
    @app.errorhandler(403)
    def access_forbidden(error):
        return render_template('home/page-403.html'), 403

def configure_db(app):
    with app.app_context():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def configure_logger(app):
    # Clear existing handlers to avoid duplicate logs
    app.logger.handlers.clear()

    # Create a file handler to write log messages to
    file_handler = logging.FileHandler(app.config['LOG_FILE'], mode='w')

    # Create a log formatter
    formatter = logging.Formatter(app.config['LOG_FORMAT'])
    file_handler.setFormatter(formatter)

    # Set the log level bases on the app's debug config
    if app.config['DEBUG']:
        app.logger.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)

    # Add the file handler to the app's logger
    app.logger.addHandler(file_handler)

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Load configuration from the Config class
    app.config.from_object(config_dict['development']) # ! Make sure to change this to 'production' when deploying

    # Initialize instances
    register_extensions(app)
    register_blueprints(app)
    set_errorhandlers(app)
    configure_db(app)
    configure_logger(app)

    return app
