from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.file import FileRequired
from wtforms import StringField
from wtforms.validators import DataRequired


class InitialRelationDataForm(FlaskForm):
    fiscalYears_CSV = FileField("Select the filled out `initialize_fiscalYears.csv` file here.", validators=[FileRequired()])
    vendors_CSV = FileField("Select the filled out `initialize_vendors.csv` file here.", validators=[FileRequired()])
    statisticsSources_CSV = FileField("Select the filled out `initialize_statisticsSources.csv` file here.", validators=[FileRequired()])


class TestForm(FlaskForm):
    string = StringField('This is a string submission field')