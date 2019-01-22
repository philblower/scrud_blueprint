from .models_chinook import *
from .models_pab import *

from . import db # from flaskr import db

#*************************************************************
# This is required to make WTForms_Alchemy work with Flask-WTF
# See :  http://wtforms-alchemy.readthedocs.io/en/latest/advanced.html#using-wtforms-alchemy-with-flask-wtf
from flask_wtf import FlaskForm
from wtforms import DateTimeField
from wtforms_alchemy import model_form_factory

BaseModelForm = model_form_factory(FlaskForm)
class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session
#*************************************************************

# models_chinook.py forms
class AlbumForm(ModelForm):
    class Meta:
        model = Album


class ArtistForm(ModelForm):
    class Meta:
        model = Artist

# models_pab.py forms
class CountryForm(ModelForm):
    class Meta:
        model = Country


class UserForm(ModelForm):
    class Meta:
        model = User


class CompanyForm(ModelForm):
    class Meta:
        model = Company


class EmployeeForm(ModelForm):
    class Meta:
        model = Employee


class PostForm(ModelForm):
    class Meta:
        model = Post
    # reformat datetime to match html5 datetime-local format
    created_on = DateTimeField(format="%Y-%m-%dT%H:%M")

class PetForm(ModelForm):
    class Meta:
        model = Pet
