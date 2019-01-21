import datetime as dt
from . import bp
from flask import render_template

""" This function is a placeholder to implement a custom dashboard for the database.

scrud/templates/base.html has a call to this blueprint and function.  The empty dashboard framework allows me to use the scrud blueprint without altering it in larger applications.
"""
@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard/dashboard.html")
