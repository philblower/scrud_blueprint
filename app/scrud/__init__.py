from flask import Blueprint

bp = Blueprint("scrud", __name__, template_folder="templates", static_folder="static")

# import views has to be after all code to avoid a circular reference when blueprint is registered
from .views import *
