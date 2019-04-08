from collections import OrderedDict
from sqlalchemy import ForeignKey, func
from sqlalchemy.ext.declarative import declared_attr
from . import db
from . import ManySideRelationship

""" The dt_column_spec in each class sets the DataTable columns to show in the table and the column titles. The form_spec sets html form input labels, type of input, placeholder values and default values.

Example dt_column_spec
---------------------

*   Outer dict key must be the column or relationship variable name.  DataTables tables will have a column displayed for each dict in the column_spec.  Enter a dict for each column that you want to show in DataTables.

    Column ordering is done on one column only.  If multiple columns have "order" set, then the last column set will be the sort order.

    dt_column_spec = OrderedDict([
        ("first_name",              # column or relationship attribute
            {"label":"First name"}
        ),
        ("last_name",
            {"label":"Last name",
            "order":"asc"}          # ascending order using this column
        ),
        ("spouse",                  # one side of relationship
            {"label":"Spouse",
            "link":True}
        ),
        ("children",                # many side of relationship
            {"label":"Children",
            "link":True}
        ),
        ("...",
            {"label":"..."}
        )
    ])

    dt_column_spec options
    ----------------------
    The specification is coded in an OrderedDict of dicts.  The outer dict key is the column name (model attribute).

        inner dict keys
        --------------
        label : DataTable column label
        link : [True, False]
            True : column value is displayed as a link to related records
            False: column is shown as a value only, will not link to related table
            Only used on relationship columns (if entered for other columns it is ignored)
            If not specified, defaults to True for relationship columns
        order : ['asc', 'desc']
            The table will be ordered using this column
            "order" should only be added to one column.  If more than one, then the order will be on the last column entered.

Example form_spec
-----------------
    * Only specify for columns that need a value from the user.
    * "id" (or primary key) is not entered in form because its value is automatically set and incremented by the database.
    * Form does not have inputs for children.  The children attribute is automatically populated by SQLAlchemy using the back relationship.
    # Form does not have an input for computed columns. Models with computed columns must override the set_computed_columns() method.

    form_spec = OrderedDict([
        ("first_name",
            {"label":"First name",
            "placeholder": "first name",    # defaults to "" if not entered
            "value":"",                     # defaults to "" if not entered
            "type": "text",
            "validate": "required"}         # defaults to "" if not entered
        ),
        ("last_name",
            {"label":"Last name",
            "placeholder": "last name",
            "type": "text"}
        ),
        ("spouse",
            {"label":"Spouse",
            "type": "dropdown"}
        ),
        ("...",
            {"label":"...",
            "placeholder": "...",
            "value":"...",
            "type": "...",
            "validate":"..."}
        )
    ])

    form_spec options
    -----------------
    The specification is coded in an OrderedDict of dicts.  The outer dict key is the column name (model attribute).

        inner dict keys
        --------------

        label : Form input field label
        placeholder : Form input field placeholder value
        value : Form input field default value.  If value = "", then placeholder value is displayed. If value is not in inner dict, then it defaults to value = "".
        type : any html <input> type - form input field defined by html standard
               dropdown - form input field is <select> list
               boolean - True/False inline radio buttons
               computed - not in form: value is computed by .py code
        validate : HTML or jQuery validate() keyword (not fully implemented yet)
"""

class All_mixin(object):
    """ This mixin is included in all of the sqlalchemy models.
    """
    __bind_key__ = "models_pab"

    @declared_attr
    def wtform_classname(cls):
        return cls.__name__ + "Form"

    def __str__(self):
        """ The return value is displayed in tables that reference this class.
        Override this in child class to return another column (ie name)
        """
        return str(self.id)

    def set_computed_columns(self):
        """Models with computed columns should override set_computed_columns() This function should call methods implemented in individual models that compute values for computed columns.
        """
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        finally:
            db.session.close()


class Employee(db.Model, All_mixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(
        db.String(255),
        nullable=False
    )
    last_name = db.Column(
        db.String(255),
        nullable=False
    )
    date = db.Column(
        db.Date,
        nullable=False,
    )
    salary = db.Column(
        db.Numeric(precision=9, asdecimal=False)
    )
    married = db.Column(
        db.Boolean(),
        nullable=False
    )

    company_id =  db.Column(db.Integer, ForeignKey("company.id", ondelete="SET NULL", onupdate="CASCADE")) # employer
    country_id = db.Column(db.Integer, ForeignKey("country.id", ondelete="SET NULL", onupdate="CASCADE"))
    dt_column_spec = OrderedDict([
        ("id",
            {"label":"pk_id"}),
        ("first_name",
            {"label":"First name"}
        ),
        ("last_name",
            {"label":"Last name",
             "order":"desc"} # ascending or descending order using this column
        ),
        ("date",
            {"label":"Date"}
        ),
        ("salary",
            {"label":"Salary"}
        ),
        ("married",
            {"label":"Married"}
        ),
        ("company_id",
            {"label":"Employer",
            "display_col":"name", # value in this column of related table is displayed
            "link":True}
        ),
        ("country_id",
            {"label":"Country",
            "display_col":"name",
            "link":False}
        )
    ])

    form_spec = OrderedDict([
        ("first_name",
            {"label":"First name",
            "placeholder": "name",
            "value":"",
            "type": "text",
            "validate": "required"}
        ),
        ("last_name",
            {"label":"Last name",
            "placeholder": "last name",
            "value":"",
            "type": "text"}
        ),
        ("date",
            {"label":"Date",
            "placeholder": "2000-01-01",
            "value":"",
            "type": "dateISO"}
        ),
        ("salary",
            {"label":"Salary",
            "placeholder": "1.00",
            "value":"",
            "type": "number"}
        ),
        ("married",
            {"label":"Married",
            "placeholder": "True",
            "value":"",
            "type": "boolean"}
        ),
        ("company_id",
            {"label":"Employer",
            "value":"",
            "type": "dropdown"}
        ),
        ("country_id",
            {"label":"Country",
            "value":"",
            "type": "dropdown"}
        )
    ])

    def __str__(self):
        return self.last_name


class Company(db.Model, All_mixin):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    industries = db.Column(db.String(255), nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)
    num_employees = db.Column(db.Integer, nullable=False)
    market_cap = db.Column(db.Float, nullable=False)
    headquarters = db.Column(db.String(255), nullable=False)
    rev_per_employee = db.Column(db.Float, nullable=True)
    employees = ManySideRelationship("Employee", "company_id")
    # The return value is displayed in tables that reference this class.
    def __str__(self):
        return self.name

    # any model with computed columns must define set_computed_columns()
    # and set_computed_columns() must call a function for each column to compute the value for that column
    def set_computed_columns(self):
        self.compute_rev_per_employee()
        super(Company, self).set_computed_columns()

    def compute_rev_per_employee(self):
        self.rev_per_employee = 1.0e9 * self.revenue / self.num_employees

    dt_column_spec = OrderedDict([
        ("id",
            {"label":"pk_id"}),
        ("rank",
            {"label": "Rank",
            "order":"desc"}),
        ("name",
            {"label": "Name"}),
        ("industries",
            {"label": "Industry"}),
        ("revenue",
            {"label": "Revenue ($B)"}),
        ("fiscal_year",
            {"label": "Fiscal Year"}),
        ("num_employees",
            {"label": "# Employees"}),
        ("market_cap",
            {"label": "Market Cap"}),
        ("headquarters",
            {"label": "Headquarters"}),
        ("rev_per_employee",
            {"label": "Rev Per Employee",
             "render":"$.fn.dataTable.render.number(',', '.', 0, '$')"}),
        ("employees",
            {"label": "Employee Table",
            "link":True})
    ])

    form_spec = OrderedDict([
        ("rank",
            {"label": "Rank",
            "placeholder": "rank",
            "type": "number",
            "validate": "required"
            }),
        ("name",
            {"label": "Name",
            "placeholder": "name",
            "type": "text"}),
        ("industries",
            {"label": "Industry",
            "placeholder": "industry",
            "type": "textarea"}),
        ("revenue",
            {"label": "Revenue",
            "placeholder": "100",
            "type": "number"}),
        ("fiscal_year",
            {"label": "Fiscal Year",
            "placeholder": "2018",
            "type": "text"
            }),
        ("num_employees",
            {"label": "# Employees",
            "placeholder": "100",
            "type": "number"
            }),
        ("market_cap",
            {"label": "Market Cap",
            "placeholder": "100",
            "type": "number"
            }),
        ("headquarters",
            {"label": "Headquarters",
            "placeholder": "Cupertino",
            "type": "text"
            })
    ])


class Country(db.Model, All_mixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
		db.String(255),
		nullable=False
	)
    political_system = db.Column(
		db.String(255),
		nullable=False
	)
    population = db.Column(db.Float, nullable=False)
    citizens = ManySideRelationship("Employee", "country_id")
    dt_column_spec = OrderedDict([
        ("id",
            {"label":"pk_id"}),
        ("name",
            {"label":"Name"}),
        ("political_system",
            {"label":"Political System"}),
        ("population",
            {"label":"Population (M)"}),
        ("citizens",
            {"label":"Citizens"})
    ])

    form_spec = OrderedDict([
        ("name",
            {"label":"Name",
            "placeholder": "name",
             "type": "text"
             }),
        ("political_system",
            {"label":"Political System",
            "placeholder": "democracy",
            "type": "text"
            }),
        ("population",
            {"label":"Population (M)",
            "placeholder": "0",
            "type": "number"
            })
    ])

    def __str__(self):
        return self.name


class User(db.Model, All_mixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(255),
        nullable=False,
        # I don't use info, but left it here as an example
        info={"description":"Name", "label":"Name"}
    )
    email = db.Column(
        db.String(255),
        nullable=False
    )
    posts = ManySideRelationship("Post", "user_id")
    pets = ManySideRelationship("Pet", "owner_id")

    dt_column_spec = OrderedDict([
        ("id",
            {"label":"pk_id"}),
        ("name",
            {"label":"Name"}),
        ("email",
            {"label":"Email"}),
        ("posts",
            {"label":"Posts",
            "link":True}),
        ("pets",
            {"label":"Pets",
            "link":True})
    ])

    form_spec = OrderedDict([
        ("name",
            {"label":"Name",
            "placeholder": "name",
            "type": "text"
            }),
        ("email",
            {"label":"Email",
            "placeholder": "me@gmail.com",
            "type": "email"
            })
    ])

    def __str__(self):
        return self.name

class Post(db.Model, All_mixin):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    user_id =  db.Column(db.Integer, ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"))
    created_at = db.Column(db.DateTime, server_default=func.now())

    dt_column_spec = OrderedDict([
        ("id",
            {"label":"pk_id"}),
        ("user_id",
            {"label":"User",
            "display_col":"name"}),
        ("body",
            {"label":"Body",
            "render": "jQuery.fn.dataTable.render.ellipsis( 17, false )"}),
        ("date",
            {"label":"Date"}),
        ("created_at",
            {"label":"Created at",
             "order":"desc"}) # descending order using this column
    ])

    form_spec = OrderedDict([
        ("user_id",
            {"label":"User",
            "type": "dropdown"
            }),
        ("body",
            {"label":"Body",
            "placeholder": "body text",
            "type": "textarea"
            }),
        ("date",
            {"label":"Date",
            "placeholder": "2019-01-01",
            "type": "date"
            }),
        # set to use server_default, so don't enter in form
        # ("created_at",
        #     {"label":"Created at",
        #     "placeholder": "datetime-local",
        #     "type": "datetime-local"}
        # )
    ])

class Pet(db.Model, All_mixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(255),
        nullable=False
    )
    animal = db.Column(
        db.String(255),
        nullable=False
    )
    owner_id =  db.Column(db.Integer, ForeignKey("user.id", ondelete="SET NULL", onupdate="CASCADE"))
    weight_lb = db.Column(
        db.Numeric(precision=5, asdecimal=False)
    )
    weight_kg = db.Column(
        db.Numeric(precision=5, asdecimal=False)
    )
    weight_st = db.Column(
        db.Numeric(precision=5, asdecimal=False)
    )

    dt_column_spec = OrderedDict([
        ("id",
            {"label":"pk_id"}),
        ("name",
            {"label":"Name"}
        ),
        ("animal",
            {"label":"Animal"}
        ),
        ("owner_id",
            {"label":"Owner1",
            "display_col":"name",
             "link":True}
        ),
        ("weight_lb",
            {"label":"Weight (lbs)",
             "order":"desc"}
        ),
        ("weight_kg",
            {"label":"Weight (kg)",
             "render":"$.fn.dataTable.render.number(',', '.', 1)"}
        ),
        ("weight_st",
            {"label":"Weight (st)",
             "render":"$.fn.dataTable.render.number(',', '.', 1)"}
        )
    ])

    form_spec = OrderedDict([
        ("name",
            {"label":"Name",
            "placeholder": "name",
            "value":"",
            "type": "text",
            "validate": "required"}
        ),
        ("animal",
            {"label":"Animal",
            "placeholder": "dog",
            "value":"",
            "type": "text",
            "validate": "required"}
        ),
        ("owner_id",
            {"label":"Owner",
            "value":"",
            "type": "dropdown",
            "validate": "required"}
        ),
        ("weight_lb",
            {"label":"Weight (lbs)",
            "placeholder": "35",
            "value":"",
            "type": "number"}
        )
    ])

    def __str__(self):
        return self.name

    def set_computed_columns(self):
        self.compute_weight_kg()
        self.compute_weight_st()
        super(Pet, self).set_computed_columns()

    def compute_weight_kg(self):
        self.weight_kg = self.weight_lb / 2.205

    def compute_weight_st(self):
        self.weight_st = self.weight_lb / 14.0
