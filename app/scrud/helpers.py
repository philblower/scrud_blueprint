from sqlalchemy import inspect
from sqlalchemy.orm import RelationshipProperty
from app import db

def str_to_bool(s):
    if s == "True" or s == "true":
        return True
    elif s == "False" or s =="false":
        return False
    elif s == "On" or s == "on":
        return True
    elif s == "Off" or s == "off":
        return False
    elif s == "":
        return None
    else:
        return s

def map_name_and_value(table_class, form_input_name, form_input_value):
    """If form input is a relationship, get the related foreign key column (i.e. company -> company_id)

    Parameters
    ----------
    table_class : sqlalchemy class
    form_input_name : str
        name of the form input (typically the foreign key relationship)
    form_input_value : str
        value returned from form input

    Returns
    -------

    Notes
    -----
    The relationship column is not in the db.  It only exists within the python sqlalchemy namespace. Get foreign key column so that I can write directly to the database.
    """
    # .property and .prop.local_columns are sqlalchemy attributes
    attr = getattr(table_class, form_input_name) # i.e. attr = Employee.company
    if type(attr.property) is RelationshipProperty:
        # get name of related foreign key column (i.e. company_id)
        name = next(iter(attr.prop.local_columns)).name
        # mysql expects an int, not a string for fk id's, set to python type None, and SQLAlchemy takes care of converting that to null.
        if form_input_value == "None": # <select> returns "None" if a selection is not made
            value = None
        else:
            value = str_to_bool(form_input_value)
    else:
        name = form_input_name
        # convert form str to python type
        value = str_to_bool(form_input_value)
    return name, value
