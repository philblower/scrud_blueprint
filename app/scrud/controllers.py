from flask import current_app
from app import db
import sys
from sqlalchemy import asc, desc, and_
from sqlalchemy.sql import select, outerjoin
from sqlalchemy.orm import aliased
from app.models_pab import *
from app.models_chinook import *
from app.forms import *
from .html import *


class TableConfig:
    """
    Lists each database and its tables and sets a unique ID number for each table.  Builds the list of dicts in the DataTable json format for each table.  Builds a list of dicts that set the sqlalchemy select and filter statements for every column in each table.

    Note that column ordering is defined in both the sqlalchemy select statement and the DataTables configuration. The sqlalchemy select statement order is not really required since DataTables will order the columns per its configuration regardless of the order of the rows from the server. I implemented the sqlalchemy order so that the tables would be ordered when using Jupyter.

    Returns
    -------
    db_tables : dict
        key = database name
        value = dict of table names in database
            key = table name
            value = unique id (uid)

        Sample db_tables:
            {'chinook.sqlite':
                {'album': 0, 'artist': 1},
             'pab.sqlite':
                {'employee': 2,
                  'company': 3,
                  'country': 4,
                  'user': 5,
                  'post': 6,
                  'pet': 7
                }
            }
    dt_tables_config : list of dicts
        Each database table is an item in the list.  The list index equals the uid, by design.

        Sample dt_tables_config :
            [
                {
                    'uid': 0,
                    'class': app.models_chinook.Album
                    'database': 'chinook.sqlite',
                    'tablename': 'album',
                    'th': ['Album ID', 'Title', 'Artist', 'Functions'],
                    'columns': [
                        {'data': 'id'},
                        {'data': 'title'},
                        {'data': 'artist'},
                        {'data': 'functions'}
                    ],
                    'render': ['', '', ''],
                    'order': [[0, 'desc']]
                },
                {
                    'uid': 1,
                    ...
                },
                ...
            ]
    """
    def __init__(self):
        uid = 0
        dt_dict = {}
        for k, v in current_app.config["SCRUD_BINDS"].items():
            t_dict = {}
            for t in db.get_tables_for_bind(bind=k):
                t_dict[t.name] = uid
                uid += 1
            dt_dict[v] = t_dict
        self.db_tables = dt_dict
        self.modules = sys.modules[__name__] # all models and forms
        self._dt_column_spec()
        self._sqlalchemy_stmt()

    def _dt_column_spec(self):
        """ Read models*.py dt_column_spec and converts to DataTables json format.

        Returns
        -------
        dt_tables_config : list of dicts
            By design, the list index equals the uid. This simplifies getting the table since can access using the index.
            dict reformat : {
                    "uid": uid,
                    "database": database name,
                    "tablename": table name,
                    "th": th, # list of column titles
                    "columns": columns, # list of column attr names
                    "placeholder_data": list of placeholder_data
                    "render": render, # list of render functions
                    "order": order
                }

        Sample format for columns, th and order keys:
        ---------------------------------------------
            # DataTables column data (model attribute for column)
            columns = [
                {'data': 'name'},
                {'data': 'email'},
                {'data': 'posts'},
                {'data': 'pets'}
            ]

            order = [ [2, "desc"] ] # index starts at zero

            # html <th> column labels
            th = [
                'Name',
                'Email',
                'Posts',
                'Pets'
            ]
        """
        dt_tables_config = [] # DataTables table configuration
        for k, v in self.db_tables.items(): # k = databasename, v = dict of tablenames:uid
            for t, uid in v.items(): # t = tablename
                class_ = getattr(self.modules, t.capitalize())

                # build list of all column <th> for .html and columns object for datatables
                th = []
                columns = []
                render =[]
                col_types = []
                row_data = {}

                # set default order to use if no column is set in models
                order = [[0, "desc"]]
                i = 0 # column index for DataTables (DT uses index, not name)
                for col, spec in class_.dt_column_spec.items():
                    th.append(spec["label"])
                    columns.append({"data": col})

                    if "order" in spec:
                        order = [[ i, spec["order"]  ]]
                    i += 1

                    # set render columns
                    if "render" in spec:
                        render.append(spec["render"])
                    else:
                        render.append("")

                # add column for update and delete functions
                th.append("Functions")
                columns.append({"data": "functions"})

                dt_table_config = {
                    "uid": uid,
                    "class_": class_,
                    "database": k,
                    "tablename": t,
                    "th": th, # column titles
                    "columns": columns, # column attr names
                    "render": render, # render functions
                    "order": order
                }
                dt_tables_config.insert(uid, dt_table_config)
        self.dt_tables_config = dt_tables_config

    def _sqlalchemy_stmt(self):
        """ Build table sqlalchemy select statement for each table in each database.  Also specifies column as one-side relationship, many-side relationship, or database value.

        Notes
        -----
        The sqlalchemy stmt construction can be done once at the start since everything needed is specified in dt_column_spec
        """
        sqlalchemy_table_stmts = [] # DataTables table configuration
        for k, v in self.db_tables.items(): # k = databasename, v = dict of tablenames:uid
            for t, uid in v.items(): # t = tablename
                class_ = getattr(self.modules, t.capitalize())

                # include pk id in all tables
                # id is used to update or delete rows (sets html data-*)
                # can be displayed or not in table based on dt_column_spec
                cols = [class_.id]

                # col_types : {"osr", "msr", "value"}
                # osr : one-side relationship; msr = many-side relationship; value = value from database table cell
                columns = []
                osr_filter = []
                j = class_.__table__ # join on parent class
                for col, spec in class_.dt_column_spec.items():
                    if "link" in spec: # models.py sets display style for column
                        link = spec["link"]
                    else:
                        link = False # default to no link if not spec'd
                    attr = getattr(class_, col)
                    if isinstance(attr, ManySideRelationship): # col is the many-side of relationship
                        fk_class = get_related_class(attr, self.modules)
                        fk = getattr(fk_class, attr.fk)
                        stmt = select([func.count(fk_class.id)]).\
                            where(class_.id == fk).\
                            as_scalar().label(col)
                        columns.append({"col_name":col, "display":stmt, "type":"msr", "pk":None, "alias":None, "link":link})
                    elif attr.foreign_keys: # col is a foreign key (one-side of relationship)
                        fk = list(attr.foreign_keys)[0]
                        fk_class = get_related_class(attr, self.modules)
                        alias = aliased(fk_class) # to avoid name ambiguity
                        pk = inspect(fk_class).primary_key[0].name
                        # build join stmt using .outerjoin chaining
                        j = j.outerjoin(alias, attr == getattr(alias, pk))
                        columns.append({"col_name":col, "display":spec["display_col"], "type":"osr",
                                        "pk":pk, "alias":alias, "link":link})
                        # get id for all foreign key columns in addition to the display name column.  ID is used to set html element data-fk_id parameter.
                        # Create a unique col_name for fk_id since there might
                        # be more than than one foreign key in model. A unique
                        # name is required so that select stmt names are
                        # unambiguous.
                        fk_id_name = "fk_id" + col
                        columns.append({"col_name":fk_id_name, "display":"id", "type":"osr", "pk":"id", "alias":alias, "link":False})
                    else: # column is a database table value
                        columns.append({"col_name":col, "display":col, "type":"value", "pk":None, "alias":None, "link":link})

                # get sqlalchemy order_by stmt
                order_stmt = getattr(class_, "id").desc()
                for col, spec in class_.dt_column_spec.items():
                    if "order" in spec:
                        if spec["order"] == "desc":
                            order_stmt = getattr(class_, col).desc()
                        else:
                            order_stmt = getattr(class_, col).asc()

                sqlalchemy_table_stmt = {
                    "uid": uid,
                    "class_": class_,
                    "database": k,
                    "tablename": t,
                    "columns": columns,
                    "osr_filter": osr_filter,
                    "osr_join": j,
                    "order_stmt": order_stmt
                }
                sqlalchemy_table_stmts.insert(uid, sqlalchemy_table_stmt)
        self.sqlalchemy_table_stmts = sqlalchemy_table_stmts

    def get_dt_tables_config(self):
        return self.dt_tables_config

    def get_sqlalchemy_table_stmts(self):
        return self.sqlalchemy_table_stmts

class LinkIDs:
    """ Sets p_uid, c_uid, row_id, fk_id, and fk prior to getting data for DataTables.

    Parameters
    ----------
    p_uid : int
        parent table uid
    c_uid : int
        child table uid
    row_id : int
        parent table row
    fk_id : int
        child table row id
    fk : str
        child table foreign key attribute (ie Employee.company_id : fk = company_id)

    Notes
    -----
    I originally tried having DataTables send the id's in its ajax call.  This did not work because it would try to reinitialize the table, which it won't do.  DataTable.ajax.reload(), which doesn't reinitialize the table, does not have an option to send new parameter values to the reload call.  This class is my work around.
    """
    def __init__(self):
        self.p_uid = None #parent table uid
        self.c_uid = None #child table uid
        self.row_id = None
        self.fk_id = None
        self.fk = None

    def set_link_ids(self, p_uid, c_uid, row_id, fk_id, fk):
        self.p_uid = p_uid
        self.c_uid = c_uid
        self.row_id = row_id
        self.fk_id = fk_id
        self.fk = fk

    def get_link_ids(self):
        return {
            "p_uid": self.p_uid,
            "c_uid": self.c_uid,
            "row_id": self.row_id,
            "fk_id": self.fk_id,
            "fk": self.fk
        }

def get_table_data():
    """ Get the data for the requested table from the database.

    Parameters
    ----------
    current_app.tc : TableConfig instance
    current_app.link_ids : LinkIDs instance

    Returns
    -------
    records_total : int
        total number of records (rows) in requested table
    records : list of dicts
        requested table data in json format required by DataTables

    Notes
    -----
    In my usage, parent refers to the table containing the link.  Child refers to the table called by the link.
    """
    link_ids = current_app.link_ids.get_link_ids()
    p_uid = link_ids["p_uid"] # parent table uid
    c_uid = link_ids["c_uid"] # child table uid, =None unless link clicked
    row_id = link_ids["row_id"] # parent table row
    fk_id = link_ids["fk_id"] # child table row id
    fk = link_ids["fk"] # parent table foreign key attr
    p_class = current_app.tc.get_dt_tables_config()[p_uid]["class_"]

    uid = p_uid # default: display parent table

    # If child table, set uid and filter
    # row_id or fk_id != None if child table
    link_table_flag = False # Default is parent table
    link_filter = None
    if fk_id: # link to child table
        c_class = current_app.tc.get_dt_tables_config()[c_uid]["class_"]
        link_filter = (c_class.id == fk_id)
        uid = c_uid # display the child table
        link_table_flag = True
    elif row_id: # link to msr table (fk_id=None, row_id = int in this case)
        msr = getattr(p_class, fk) # returns ManySideRelationship class
        related_class = getattr(current_app.tc.modules, msr.related_classname)
        fk_col = getattr(related_class, msr.fk) # i.e. Employee.company_id
        link_filter = (fk_col == row_id)
        uid = c_uid
        link_table_flag = True

    # get requested table from database
    t = current_app.tc.get_sqlalchemy_table_stmts()[uid] # for table to display

    # build select stmt
    # get columns for select
    sel_cols = []
    for col in t["columns"]:
        if col["type"] == "osr":
            # need to rename fk_id to avoid key name ambiguity since there
            # can be more than one fk in a model
            if "fk_id" in col["col_name"]:
                attr = getattr(col["alias"], col["pk"]).label(col["col_name"])
            else:
                attr = getattr(col["alias"], col["display"]).label(col["col_name"])
        elif col["type"] == "msr":
            attr = col["display"].label(col["col_name"])
        else: # value from database
            attr = getattr(t["class_"], col["display"]).label(col["col_name"])
        sel_cols.append(attr)

    # combine select, join (select_from) and where stmts into one sqlalchemy statement
    if link_table_flag: # child table
        s = select(sel_cols, use_labels=True)\
            .select_from(t["osr_join"])\
            .where(link_filter)\
            .order_by(t["order_stmt"])
    else: # parent table
        s = select(sel_cols, use_labels=True)\
            .select_from(t["osr_join"])\
            .order_by(t["order_stmt"])

    conn = db.get_engine(bind=t["class_"].__bind_key__).connect()
    result = conn.execute(s)

    # build records as list of dicts in format required by DataTables
    records = [{k:v for k, v in row.items()} for row in result]

    # add update and delete functions to each row
    for r in records:
        r["functions"] = set_function_icon_html(r["id"], uid)

    # for each record, and each column, check if the column is a link
    # if so, then set the link str and html data-* parameters for that row/column.
    for r in records:
        for spec in t["columns"]:
            if spec["link"]:
                col_name = spec["col_name"]
                row_id = r["id"]
                link_str = r[col_name] # the column value
                fk = col_name # ie company_id
                if spec["type"] == "msr":
                    fk_id = None
                    r[col_name] = set_table_link_html(uid, row_id, fk_id, fk, link_str)
                elif spec["type"] == "osr":
                    # see _sqlalchemy_stmt() for fk_id column name convention
                    display_value = r["fk_id" + col_name]
                    if display_value: #display_value=None if db value=null
                        fk_id = r["fk_id" + col_name]
                        r[col_name] = set_table_link_html(uid, row_id, fk_id, fk, link_str)
                    else: # null value in db
                        r[col_name] = "None"

    # get total records in table for DataTables footer
    records_total = db.session.query(t["class_"].id).count()
    return records_total, records
