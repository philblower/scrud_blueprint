from collections import OrderedDict
from sqlalchemy import ForeignKey, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.inspection import inspect
from . import db
from . import ManySideRelationship

""" Changes to sqlite chinook database:
1. All primary key names set to "id"
"""

class All_mixin(object):
    """ This mixin is included in all of the sqlalchemy models.
    """
    # do not use bind_key because I'm using these models as default
    # sqlalchemy database URI.
    __bind_key__ = None

    # all WTForm classes will be name "model_classnameForm" by convention
    @declared_attr
    def wtform_classname(cls):
        return cls.__name__ + "Form"

    def __str__(self):
        """ The return value is displayed in tables that reference this class.
        Override this in child class to return another column (ie name).

        Returns
        -------
        primary key value : str(int)
        """
        pk = inspect(self).identity
        return str(pk)

    def set_computed_columns(self, **kwargs):
        """Models with computed columns should override set_computed_columns() This function will call methods implemented in individual models that compute values for computed columns.
        """
        pass

class Album(db.Model, All_mixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(
        db.String(160),
        nullable=False
    )

    artistid =  db.Column(db.Integer, ForeignKey("artist.id", ondelete="SET NULL", onupdate="SET NULL"))
    dt_column_spec = OrderedDict([
        ("id",
            {"label":"Album ID"}
        ),
        ("title",
            {"label":"Title"}
        ),
        ("artistid",
            {"label":"Artist",
            "display_col":"name",
            "link":True}
        )
    ])

    form_spec = OrderedDict([
        ("title",
            {"label":"Title",
            "placeholder": "title",
            "value":"",
            "type": "text"}
        ),
        ("artistid",
            {"label":"Artist",
            "placeholder": "",
            "value":"",
            "type": "dropdown"}
        )
    ])

    # can override __str__ if want a custom value displayed as the link
    # def __str__(self):
    #     return self.title

class Artist(db.Model, All_mixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(120),
        nullable=True
    )
    albums = ManySideRelationship("Album", "artistid")
    dt_column_spec = OrderedDict([
        ("id",
            {"label":"Artist ID"}
        ),
        ("name",
            {"label":"Name"}
        ),
        ("albums",
            {"label":"Albums",
            "link":True}
        )
    ])

    form_spec = OrderedDict([
        ("name",
            {"label":"Name",
            "placeholder": "Beethoven",
            "value":"",
            "type": "text"}
        )
    ])

    def __str__(self):
        return self.name
