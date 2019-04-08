from sqlalchemy import inspect
from flask import current_app
from app import ManySideRelationship

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

def get_related_class(attr, modules):
    """ Get the class referenced by a model attribute.

    Parameters
    ----------
    attr : model column (sqlalchemy Column, ManySideRelationship class, sqlalchemy Column Foreign Key)
    modules : sys.modules[__name__]
        all loaded models and forms from TableConfig

    Returns
    -------
    class_ : sqlalchemy class
        related (child) class if one exists
    """
    if isinstance(attr, ManySideRelationship): # col is the many-side of relationship
        # check for isinstance of ManySideRelationship first, because attr.foreign_keys will fail if done on MSR
        return getattr(modules, attr.related_classname)
    elif attr.foreign_keys: # col is a foreign key (one-side of relationship), returns empty set if not a fk
        fk = next(iter(attr.expression.foreign_keys)) #fk is in a set, so next(iter()) gets item from set
        return getattr(modules, fk._table_key().capitalize())

def get_uid_from_tablename(tablename):
    """ Get the uid for the given tablename

    Parameters
    ----------
    tablename : str
        table name

    Returns
    -------
    uid : int
        table unique id

    Note
    ----
    This assumes (and I've probably implicitly made this assumption in other code) that there isn't a table by the same name in another database.
    """
    class_ = getattr(current_app.tc.modules, tablename.capitalize())
    database = current_app.config["SCRUD_BINDS"][getattr(class_, "__bind_key__")]
    return current_app.tc.db_tables[database][tablename]
