from flask import Blueprint

""" This blueprint is a placeholder to implement a custom dashboard for the database.

scrud/templates/base.html has a call to this blueprint and function.  The empty dashboard framework allows me to use the scrud blueprint without altering it in larger applications.
"""

bp = Blueprint("dashboard", __name__, template_folder="templates", static_folder="static")

from . import views
