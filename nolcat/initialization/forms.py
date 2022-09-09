from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.file import FileRequired
from wtforms.fields import MultipleFileField
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


class AUCTAndCOUNTERForm(FlaskForm):
    """Creates a form for uploading the `annualUsageCollectionTracking` relation data and the reformatted COUNTER R4 TSV files."""
    annualUsageCollectionTracking_TSV = FileField("Select the filled out \"initialize_annualUsageCollectionTracking.tsv\" file here.", validators=[FileRequired(), DataRequired()])
    COUNTER_TSVs = MultipleFileField("Select the reformatted R4 reports. If all the files are in a single folder and that folder contains no other items, navigate to that folder, then use `Ctrl + a` to select all the files in the folder.", validators=[FileRequired(), DataRequired()])  #ToDo: Double check that validators don't cause problems with multiple file selection