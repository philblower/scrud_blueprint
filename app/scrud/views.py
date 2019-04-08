from flask import (
    Blueprint, render_template, request, current_app
)
from flask import json
import sys
import datetime as dt
from sqlalchemy import desc
from sqlalchemy.inspection import inspect

from . import bp
from app import db
from .controllers import (TableConfig, LinkIDs, get_table_data)
from .html import set_form_html
from .helpers import str_to_bool, get_uid_from_tablename

@bp.before_app_first_request
def init_table_configuration():
    """ Run once to initialize the table configuration class
    """
    current_app.tc = TableConfig()
    current_app.link_ids = LinkIDs()

@bp.route("/")
@bp.route("/index")
def index():
    """
    Parameters
    ----------
    """
    menumap = current_app.tc.db_tables
    dt_tables_config = current_app.tc.get_dt_tables_config()
    return render_template("scrud/index.html", menumap=menumap, dt_tables_config=dt_tables_config)

@bp.route("/set_link_ids", methods=["GET", "POST"])
def set_link_ids():
    """ Sets uid, row_id, fk_id, and fk prior to getting data for DataTables.  A row in a table may have links to other tables. This sets the parameters for those links.

    Notes
    -----
    I originally tried having DataTables send the id's in its ajax call.  This did not work because it would try to reinitialize the table, which it does not allow.  DataTable.ajax.reload(), which doesn't reinitialize the table, does not have an option to send new parameter values to the reload call.  This class is my work around.
    """
    dt_request = request.get_json()

    p_uid = int(dt_request['p_uid']) # parent table uid
    row_id = dt_request['row_id']
    fk_id = dt_request['fk_id']
    fk = dt_request['fk'] # fk is a str in both .js and .py

    if isinstance(row_id, str):
        row_id = None if row_id == 'None' else int(row_id)
    if isinstance(fk_id, str):
        fk_id = None if fk_id == 'None' else int(fk_id)

    p_class = current_app.tc.get_dt_tables_config()[p_uid]["class_"]
    c_uid = None # default is parent table
    if fk_id: # get child table uid (both osr and msr define row_id)
        for c in list(inspect(p_class).columns):
            if c.name == fk:
                insp = inspect(c)
                fk = next(iter(insp.foreign_keys))
        c_uid = get_uid_from_tablename(fk._table_key())
    elif row_id: # msr table
        msr = getattr(p_class, fk) # returns ManySideRelationship class
        c_uid = get_uid_from_tablename(msr.related_classname.lower())

    current_app.link_ids.set_link_ids(p_uid, c_uid, row_id, fk_id, fk)
    json_dump = json.dumps({
        "c_uid": c_uid
    }, default=str)
    return json_dump

@bp.route("/init_table", methods=["GET", "POST"])
def init_table():
    """ Get the table specifications for columns, etc and send to scrud.js.
    """
    link_ids = current_app.link_ids.get_link_ids()
    uid = link_ids["p_uid"] # table uid
    if link_ids["row_id"]: uid = link_ids["c_uid"]

    # Get table and its specs from Tables
    t = current_app.tc.get_dt_tables_config()[uid] # the requested table

    # Prep data to send to scrud.js
    json_dump = json.dumps({
        "columns": t["columns"],
        "order": t["order"],
        "render":t["render"]
    }, default=str)
    return json_dump

@bp.route("/get_data", methods=["GET", "POST"])
def get_data():
    """ Get server side processing data requested by scrud.js. Get, slice, order, format and return data requested by scrud.js.
    """
    # Prepare data to return to scrud.js
    records_total, requested_data = get_table_data()
    dt_request = request.get_json()

    json_dump = json.dumps({
        "data"    : requested_data
    }, default=str)
    return json_dump

@bp.route("/delete_record", methods=["GET"])
def delete_record():
    """
    Parameters
    ---------
    """
    id = int(request.args.get("id"))
    uid = request.args.get("uid")

    # get model class_ from uid
    class_ = current_app.tc.get_dt_tables_config()[int(uid)]["class_"]
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
    id : int
        pk id of row to edit
    uid : int
        unique id of db table
    """
    dt_request = request.get_json()

    uid = int(dt_request['uid'])
    id = None if isinstance(dt_request['id'], str) else int(dt_request['id'])

    # get table and model class_
    t = current_app.tc.get_dt_tables_config()[uid]
    class_ = t["class_"]

    if id: # update record
        q = class_.query.filter_by(id = id).first()
        if q is None:
            result  = "error"
            message = f"Did not find record with id = {id}"
        else:
            # get the html string that defines modal content
            form_html, modal_title = set_form_html(class_, q, "update")
            result  = "success"
            message = "query success"
    else: # create record
        form_html, modal_title = set_form_html(class_, "None", "create")
        result  = "success"
        message = ""

    data = {
      "result" : result,
      "table" : t["tablename"],
      "modal_title" : modal_title,
      "form_html" : form_html,
    }
    # Convert dict to JSON array
    return json.dumps(data, default=str)#, use_decimal=True)

@bp.route("/update_db", methods=["GET", "POST"])
def update_db():

    """ Create or update record in database table to values from form.

    Parameters
    ----------
    id : str (is converted to an int in this function)
        database table primary key (id)
    uid : str (is converted to an int in this function)
        table unique id
    rf : serialized form data
        form input values

    Notes
    -----
    If "id" = None then create record, else update record
    """
    id = request.args.get("id")
    uid = request.args.get("uid")
    rf = request.form

    class_ = current_app.tc.get_dt_tables_config()[int(uid)]["class_"]

    # get form class and validate with WTForms
    form_class = getattr(current_app.tc.modules, class_.wtform_classname)

    if id == "None": # create record
        create_record_flag = True
        record = class_() # get a new empty record
        form = form_class(rf)
        validated = form.validate()
    else: # update record
        create_record_flag = False
        record = class_.query.filter_by(id = int(id)).first()
        if record is None:
            result  = "error"
            message = "Did not find record with id = {}".format(id)
        # see https://wtforms-alchemy.readthedocs.io/en/latest/validators.html
        # for using unique validator with existing objects
        form = form_class(obj=record)
        form.populate_obj(record) # debug: does the line above already do this?
        validated = form.validate()

    print(form.errors, "validated = {}".format(validated))
    if request.method == "POST" and validated:
        # loop through all input fields from form
        for name, value in rf.items():
            # convert date str to datetime if using sqlite database
            if name == "date" and current_app.config["DATABASE"]=="sqlite":
                value = dt.datetime.strptime(value, "%Y-%m-%d")
            value = str_to_bool(value)
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
            record = class_.query.order_by(desc(class_.id)).first()
        else:
            record = class_.query.filter_by(id = int(id)).first()

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
