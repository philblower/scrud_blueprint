# SCRUD Blueprint

## To run :
~~~
$ ./run.sh
~~~

or manually enter the commands :
~~~
    $ export FLASK_APP=app
    $ export FLASK_ENV=development
    $ flask run
~~~

## Platform

Python 3.7, Flask, SQLAlchemy, WTForms, jQuery, Bootstrap 3.3.7, DataTables

The example database uses the Album and Artist tables from the Chinook database (models_chinook.py) and a custom database (models_pab.py). I entered the models_pab database to show how to set up multiple databases.  The company table in models_pab also shows how to implement database columns whose values are computed (not entered in form).

## Capabilities

Search, create, read, update and delete records in one or more databases.

Specify tables and forms in the models.py and forms.py files.  The columns shown in the tables and the inputs in create/update forms are controlled by python dictionaries that are added to each model class (SQLAlchemy class).  None of the files in the 'scrud' directory have to be modified except scrud/views.py. The .js, .css files and html template files can be used as is.  The only modifications required to scrud/views.py are to import the models.py classes and forms classes.  For the example used here, these import statements are:

    ~~~
    # import models and forms to populate sys.modules[__name__]
    from app.models_chinook import *
    from app.models_pab import *
    from app.forms import *
    ~~~

The app contains a dashboard blueprint that is empty.  This is included only as the base for a dashboard that could be implemented to show analytical data derived from the database data.

## Workflow to add a new table

1. Add table class to model.py
2. Add form class to form.py
3. Migrate database

## Example : Add table 'pet' to models_pab.py
See notes at top of models_pab.py for detailed descriptions of the dt_column_spec and form_spec dictionaries.

Start by checking out tag v0.1.0 from github.  This is the version without the 'pet' table.

Add a table named 'pet' to the database.  It will have columns for name, animal, owner, weight (lbs), weight (kg), weight (st).  The owner will be a link to a person from the user table.  This will demonstrate using a foreign key and SQLAlchemy relationship.  The weight (kg) and weight (st) columns provide a simple case to show how to enter columns whose values are calculated (not entered from a form).

1. Add Pet class to models_pab.py
    1. Use Flask-SQLAlchemy base class and add dt_column_spec and form_spec to this class.  (It's probably easiest to copy one of the existing classes and modify it).
    2. Override set_computed_columns() and add the functions to compute the column values to the 'Pet' class. (Only do this if there are computed columns).
    3. Override \__str\__() to set the column with values that will be shown in dropdown lists.
    ~~~
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
        owner = relationship("User", back_populates="pets", uselist=True)
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
            ("name",
                {"label":"Name"}
            ),
            ("animal",
                {"label":"Animal"}
            ),
            ("owner",
                {"label":"Owner",
                 "link":True}
            ),
            ("weight_lb",
                {"label":"Weight (lbs)"}
            ),
            ("weight_kg",
                {"label":"Weight (kg)"}
            ),
            ("weight_st",
                {"label":"Weight (st)"}
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
            ("owner",
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
    ~~~
2. Add relationship attribute for 'pets' to 'User' class.
    ~~~
    pets = relationship("Pet", back_populates="owner", lazy="select")
    ~~~
3. If you want to display a link to 'pets' in the User DataTable add a dict item to User.dt_column_spec.
    ~~~
   ("pets",
    {"label":"Pets"})
    ~~~
4. Add PetForm class to forms.py. This class sets WTForms to the default behavior for server side validation.
    ~~~
    class PetForm(ModelForm):
        class Meta:
            model = Pet
    ~~~
5. Migrate and upgrade database (if using more than one database, use ''$flask db init --multidb' to initialize migration repository).
    ~~~
    $flask db migrate
    $flask db upgrade
    ~~~

The new table will be added automatically to the database's dropdown menu in the menu bar.  Open web app, select 'pet' and create some new records.

## Workflow to add another database
1. Add another models_name.py file to define the tables in the additional database
2. Add database/models_name to SQLALCHEMY_BINDS and SCRUD_BINDS in the config.py file
3. Add a form class for each new table to the forms.py file
4. Add 'from . models_name import *' to bottom of app/__init__.py
5. Add 'from . models_name import *' to top of app/forms.py
6. Add 'from app.models_name import *' to top of app/scrud/views.py

## Constraints

1. Each table must have a non-compound primary key named 'id'
2. Table names must be all lowercase.  The model class name must be the table name capitalized.

## Conventions

1. Each model class can override the function def \__str\__(self).  This string returned by this function is displayed in dropdown lists that are used to select records from the database table.

## Unfinished Business

1. Form validation : I put in the most rudimentary data for WTForms, but haven't yet implemented proper client or server side form validation. DataTables Editor is an option for form generation and validation, but I have not looked into this in any detail.
2. The html.py file builds html strings for form inputs.  I implemented code only for html input types that were required for my current project.

## Warnings

I built this as support for my own personal needs.  There are a LOT of capabilities that a full SCRUD web app should have that are missing.  The only capabilities it does have are those I needed for my purposes.
1. Unittests : None
2. Security : I put no effort into building security into this web app.  It uses the Flask server implementation which is not suited for production code.

## References

1. Grinberg Miguel, "Flask Web Development", 2nd edition, O'Reilly, 2018
2. https://www.sitepoint.com/creating-a-scrud-system-using-jquery-json-and-datatables/  Used as a model for css and some jQuery code.
