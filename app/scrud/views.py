from flask import (
    Blueprint, render_template, request, current_app
)
# import simplejson as json
from flask import json
# import importlib
import sys
import datetime as dt
from sqlalchemy import desc
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.dynamic import AppenderQuery

from . import bp
from app import db

from .html import set_form_html, set_function_icon_html
from .html import set_table_link_html
from .helpers import map_name_and_value, str_to_bool

# import models and forms to populate sys.modules[__name__]
from app.models_chinook import *
from app.models_pab import *
from app.forms import *

@bp.route("/")
@bp.route("/index")
def index():
    """
    Parameters
    ----------
    """
    databases = {v:[t.name for t in db.get_tables_for_bind(bind=k)] for k, v in current_app.config["SCRUD_BINDS"].items()}
    return render_template("scrud/index.html", databases=databases)

@bp.route("/table_view", methods=["GET", "POST"])
def table_view():
    """
    Parameters
    ----------
    database : str
        name of mysql database with table to display
    table : str
        name of mysql table to display
    row_id : int
        id of the table row containing the link
    link_id : int
        if filter = "fk", this id is not used and is set = 0
        if filter = "pk", this is id of record pointed to by link
    key : str
        if foreign key: name of foreign key column (ie "company_id")
        if primary key: "id"
    filter : str
        all : get all rows of table
        pk : get row given by link_id
        fk : get row's from child table where the child_table.key == row_id
    """
    database = request.args.get("database")
    table = request.args.get("table")
    row_id = request.args.get("row_id") # record id of parent table row
    link_id = request.args.get("link_id")
    key = request.args.get("key") # name of primary or foreign key column
    filter = request.args.get("filter")
    print("PAB> database = {}, table = {}, row_id = {}, key = {} filter = {}".format(database, table, row_id, key, filter))

    # get model class_ from classname
    class_ = getattr(sys.modules[__name__], table.capitalize())
    relationships = inspect(class_).relationships #list of all relationship attributes in model

    # build the datatable column specification from the model dt_column_spec
    datatable_column_spec = []
    for model_attr, spec in class_.dt_column_spec.items():
        if "render" in spec:
            datatable_column_spec.append(
                {"title":spec["label"],
                "data":model_attr,
                "render":spec["render"]
                })
        else:
            datatable_column_spec.append(
                {"title":spec["label"],
                "data":model_attr
                })

    # construct the query
    if filter == "all":
        query = class_.query.order_by(class_.id).all()
    elif filter == "fk":
        fk_col = getattr(class_, key) # i.e. Employee.company_id
        query = class_.query.filter(fk_col == int(row_id)).order_by(class_.id)
    elif filter == "pk":
        query = class_.query.filter_by(id = link_id)

    # Build DataTables input : looping through q provides all rows
    # Internal loop on columns gets values for each cell or builds links
    # After db table columns are added, add the final column
    # which holds the update and delete buttons.
    records = []
    for q in query:
        # builds dict for each record in DataTables format, like below
        # {"name":q.name, "political_system":q.political_system, "population":q.population}
        record_dict = {}

        # Set links to child tables
        for model_attr, spec in class_.dt_column_spec.items():
            # check if this column is a relationship
            if model_attr in relationships: # show link in column
                # this sets r_id, r_key and r_filter for the relationship
                # get remote side for relationship
                # key will be primary key if this is one side of relationship
                # key will be foreign key if this is many side of relationship
                # remote_side returns set of relationship Column definitions
                # it only returns one column because model_attr selects only one relationship
                tablename = getattr(relationships, model_attr).table.name
                rs = getattr(relationships, model_attr).remote_side
                q_model_attr = getattr(q, model_attr)
                if not "link" in spec: # if link is not specified, then default to making the relationship a link in the table column.
                    spec["link"] = True
                r_id = q.id # id of parent table row
                if next(iter(rs)).primary_key:  #if true, this is the one side
                    if not len(q_model_attr): # NULL value in database, no children
                        link_str = "na"
                        record_dict[model_attr] = "na" # not a link
                    else:
                        link_str = q_model_attr[0].__str__()
                        link_id = q_model_attr[0].id
                        r_filter = "pk"
                        r_key = "id"
                        if spec["link"]: # make link
                            record_dict[model_attr] = set_table_link_html(database, tablename, link_str, r_id, link_id, r_key, r_filter)
                        else: # no link
                            record_dict[model_attr] = link_str
                else: # the many side of relationship
                    r_filter = "fk"
                    num_children = len(q_model_attr)
                    if not num_children:  # there are not any children
                        record_dict[model_attr] = "na" # not a link
                    else: # there are one or many children, link to child table
                        if num_children == 1: #make link == __str__
                            link_str = q_model_attr[0].__str__()
                        else: # link is number of children
                            link_str = num_children
                        r_key = next(iter(rs)).key # ie company_id
                        link_id = 0 # not used in fk relationship
                        if spec["link"]: # make link
                            record_dict[model_attr] = set_table_link_html(database, tablename, link_str, r_id, link_id, r_key, r_filter)
                        else: # no link
                            record_dict[model_attr] = link_str
            else: # get value for row/col from q (mysql table query)
                value = getattr(q, model_attr)
                record_dict[model_attr] = value

        # add update and delete functions to each row
        record_dict["functions"] = set_function_icon_html(q.id, table)
        records.append(record_dict)

    # add column for update and delete functions
    datatable_column_spec.append({"title": "", "data": "functions", "className": "functions"})

    # Prepare data to return to javascript
    data = {
        "result" : "success",
        "database" : database,
        "table" : table.lower(),
        "columns" : datatable_column_spec,
        "data"    : records
    }
    # Convert dict to JSON array
    return json.dumps(data, default=str)#, use_decimal=True)

@bp.route("/delete_record", methods=["GET"])
def delete_record():
    """
    Parameters
    ---------
    """
    id = int(request.args.get("id"))
    table = request.args.get("table")

    # get model class_ from classname
    class_ = getattr(sys.modules[__name__], table.capitalize())
    q = class_.query.filter_by(id = id).first()
    if q is None:
        result  = "error"
        message = "Did not find record with id = {}".format(id)
    else:
        try:
            db.session.delete(q)
            db.session.commit()
            result  = "success"
            message = "delete successful"
        except Exception as ex:
            db.session.rollback()
            result  = "error"
            message = ex
        finally:
            db.session.close()
    data = {
        "result" : result,
        "message" : message
    }
    # Convert dict to JSON array
    return json.dumps(data, default=str)#, use_decimal=True)

@bp.route("/get_form", methods=["GET", "POST"])
def get_form():
    """
    Parameters
    ---------
    """
    id = request.args.get("id")
    table = request.args.get("table")

    # get model class_ from classname
    class_ = getattr(sys.modules[__name__], table.capitalize())

    if id == "None": # create record
        form_html, modal_title = set_form_html(class_, "None", "create")
        result  = "success"
        message = ""
    else: # update record
        q = class_.query.filter_by(id = int(id)).first()
        if q is None:
            result  = "error"
            message = "Did not find record with id = {}".format(id)
        else:
            # get the html string that defines modal content
            form_html, modal_title = set_form_html(class_, q, "update")
            result  = "success"
            message = "query success"

    data = {
      "result" : result,
      "table" : table,
      "modal_title" : modal_title,
      "form_html" : form_html,
    }
    # Convert dict to JSON array
    return json.dumps(data, default=str)#, use_decimal=True)

@bp.route("/update_db", methods=["GET", "POST"])
def update_db():

    """ Create or update record in database table to values from form.
    If "id" = None then create record, else update record

    Parameters
    ---------
    """
    id = request.args.get("id")
    table = request.args.get("table")
    rf = request.form
    model_class = getattr(sys.modules[__name__], table.capitalize())

    # get form class and validate with WTForms
    form_class = getattr(sys.modules[__name__], model_class.wtform_classname)

    if id == "None": # create record
        create_record_flag = True
        record = model_class() # get a new empty record
        form = form_class(request.form)
        validated = form.validate()
    else: # update record
        create_record_flag = False
        record = model_class.query.filter_by(id = int(id)).first()
        if record is None:
            result  = "error"
            message = "Did not find record with id = {}".format(id)
        # see https://wtforms-alchemy.readthedocs.io/en/latest/validators.html
        # for using unique validator with existing objects
        form = form_class(obj=record)
        form.populate_obj(record) # debug: does the line above already do this?
        validated = form.validate()

    if request.method == "POST" and validated:
        # loop through all input fields from form
        for name, value in request.form.items():
            # convert date str to datetime if using sqlite database
            if name == "date" and current_app.config["DATABASE"]=="sqlite":
                value = dt.datetime.strptime(value, "%Y-%m-%d")
            name, value = map_name_and_value(model_class, name, value)
            setattr(record, name, value)

        try:
            if create_record_flag: # create record
                db.session.add(record)
                message = "Record added to database"
            else: # update record
                message = "Record updated in database"
            db.session.commit()
            result  = "success"
        except:
            db.session.rollback()
            result = "error"
            message = "Failed to create or update record"
            raise
        finally:
            db.session.close()

        # Update computed columns (computed columns are not in forms)
        if create_record_flag:
            # get the table row that was added above
            # I committed and then requeried so I could use the same
            # code for both create and update record
            record = model_class.query.order_by(desc(model_class.id)).first()
        else:
            record = model_class.query.filter_by(id = int(id)).first()

        record.set_computed_columns()
    else:
        result = "error"
        if not validated:
            message = "Form entries failed server validation. Validation =  {}".format(validated)
        else:
            message = "Request method != POST. request.method = {}.".format(request.method)

    data = {
        "result" : result,
        "message" : message
    }
    return json.dumps(data, default=str)#, use_decimal=True)
