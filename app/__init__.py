"""
    SCRUD Blueprint for Flask
"""

__version__ = "0.1.1a"

import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_bootstrap import WebCDN
from flask_migrate import Migrate
from config import conf

db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate()

def create_app(test_config=None):
    print("PAB> Python version {}".format(sys.version))

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

# Flask-migrate needs all models to build migration.  Must be added after db is created to avoid circular reference since models.py also imports db
from . models_chinook import *
from . models_pab import *
from . forms import *
