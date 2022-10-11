from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.file import FileRequired
from wtforms.fields import MultipleFileField
from wtforms.validators import DataRequired


class InitialRelationDataForm(FlaskForm):
    """Creates a form for uploading the non-usage database initialization data."""
    fiscalYears_TSV = FileField("Select the filled out \"initialize_fiscalYears.tsv\" file here.", validators=[FileRequired(), DataRequired()])
    vendors_TSV = FileField("Select the filled out \"initialize_vendors.tsv\" file here.", validators=[FileRequired(), DataRequired()])
    vendorNotes_TSV = FileField("Select the filled out \"initialize_vendorNotes.tsv\" file here.", validators=[FileRequired(), DataRequired()])
    statisticsSources_TSV = FileField("Select the filled out \"initialize_statisticsSources.tsv\" file here.", validators=[FileRequired(), DataRequired()])
    statisticsSourceNotes_TSV = FileField("Select the filled out \"initialize_statisticsSourceNotes.tsv\" file here.", validators=[FileRequired(), DataRequired()])
    statisticsResourceSources_TSV = FileField("Select the filled out \"initialize_statisticsResourceSources.tsv\" file here.", validators=[FileRequired(), DataRequired()])
    resourceSources_TSV = FileField("Select the filled out \"initialize_resourceSources.tsv\" file here.", validators=[FileRequired(), DataRequired()])
    resourceSourceNotes_TSV = FileField("Select the filled out \"initialize_resourceSourceNotes.tsv\" file here.", validators=[FileRequired(), DataRequired()])


class AUCTAndCOUNTERForm(FlaskForm):
    """Creates a form for uploading the `annualUsageCollectionTracking` relation data and the reformatted COUNTER R4 TSV files."""
    annualUsageCollectionTracking_TSV = FileField("Select the filled out \"initialize_annualUsageCollectionTracking.tsv\" file here.", validators=[FileRequired(), DataRequired()])
    COUNTER_TSVs = MultipleFileField("Select the reformatted R4 reports. If all the files are in a single folder and that folder contains no other items, navigate to that folder, then use `Ctrl + a` to select all the files in the folder.", validators=[FileRequired(), DataRequired()])  #ToDo: Double check that validators don't cause problems with multiple file selection