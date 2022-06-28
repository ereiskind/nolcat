from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.file import FileRequired
from wtforms import StringField
from wtforms.validators import DataRequired


class InitialRelationDataForm(FlaskForm):
    fiscalYears_CSV = FileField("Select the filled out `initialize_fiscalYears.csv` file here.", validators=[FileRequired()])
    vendors_CSV = FileField("Select the filled out `initialize_vendors.csv` file here.", validators=[FileRequired()])
    vendorNotes_CSV = FileField("Select the filled out `initialize_vendorNotes.csv` file here.", validators=[FileRequired()])
    statisticsSources_CSV = FileField("Select the filled out `initialize_statisticsSources.csv` file here.", validators=[FileRequired()])
    statisticsSourceNotes_CSV = FileField("Select the filled out `initialize_statisticsSourceNotes.csv` file here.", validators=[FileRequired()])
    statisticsResourceSources_CSV = FileField("Select the filled out `initialize_statisticsResourceSources.csv` file here.", validators=[FileRequired()])
    resourceSources_CSV = FileField("Select the filled out `initialize_resourceSources.csv` file here.", validators=[FileRequired()])
    resourceSourceNotes_CSV = FileField("Select the filled out `initialize_resourceSourceNotes.csv` file here.", validators=[FileRequired()])