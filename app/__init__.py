"""
    SCRUD Blueprint for Flask
"""

__version__ = "0.2.1"

import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_bootstrap import WebCDN
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate()

def create_app(run_config):
    print("PAB> Python version {}".format(sys.version))
    conf = config[run_config]

    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(conf)
    conf.init_app(app) # init_app is currently empty, this is a placeholder

    bootstrap.init_app(app)
    # use jquery 3.3.1 instead of 1.10
    app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
    '//cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/')

    db.init_app(app)
    migrate.init_app(app, db)

    #register blueprints
    from app.scrud import bp as scrud_bp
    from .dashboard import bp as dashboard_bp
    app.register_blueprint(scrud_bp, url_prefix="/scrud")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    # make "/" and "/index" show dashboard
    app.add_url_rule("/", endpoint="dashboard.dashboard")
    app.add_url_rule("/index", endpoint="dashboard.dashboard")
    return app

class ManySideRelationship:
    """ Instances of this class are used in models.py to define the many side of a relationship.  The one-side of a relationship is defined by the foreign key column in the model.

    Parameters
    ----------
    model : str
        name of sqlalchemy model in models*.py with one-side of relationship
    fk : str
        name of foreign key attr in related model

    Example
    -------
    Employee.company_id
    Company : related_classname = "Employee", fk = "company_id"
    """
    def __init__(self, related_classname, fk):
        self.related_classname = related_classname
        self.fk = fk

# Flask-migrate needs all models to build migration.  Must be added after db is created to avoid circular reference since models.py also imports db.
from . models_chinook import *
from . models_pab import *
from . forms import *
