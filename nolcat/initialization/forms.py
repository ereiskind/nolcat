from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms.fields import MultipleFileField
from wtforms.validators import DataRequired


class InitialRelationDataForm(FlaskForm):
    """Creates a form for uploading the non-usage database initialization data."""
    fiscalYears_CSV = FileField("Select the filled out \"initialize_fiscalYears.csv\" file here.", validators=[DataRequired()])
    vendors_CSV = FileField("Select the filled out \"initialize_vendors.csv\" file here.", validators=[DataRequired()])
    vendorNotes_CSV = FileField("Select the filled out \"initialize_vendorNotes.csv\" file here.", validators=[DataRequired()])
    statisticsSources_CSV = FileField("Select the filled out \"initialize_statisticsSources.csv\" file here.", validators=[DataRequired()])
    statisticsSourceNotes_CSV = FileField("Select the filled out \"initialize_statisticsSourceNotes.csv\" file here.", validators=[DataRequired()])
    resourceSources_TSV = FileField("Select the filled out \"initialize_resourceSources.tsv\" file here.", validators=[DataRequired()])
    resourceSourceNotes_TSV = FileField("Select the filled out \"initialize_resourceSourceNotes.tsv\" file here.", validators=[DataRequired()])
    statisticsResourceSources_CSV = FileField("Select the filled out \"initialize_statisticsResourceSources.csv\" file here.", validators=[DataRequired()])


class AUCTAndCOUNTERForm(FlaskForm):
    """Creates a form for uploading the `annualUsageCollectionTracking` relation data and the reformatted COUNTER R4 TSV files."""
    annualUsageCollectionTracking_TSV = FileField("Select the filled out \"initialize_annualUsageCollectionTracking.tsv\" file here.", validators=[DataRequired()])
    COUNTER_reports = MultipleFileField("Select the COUNTER report workbooks. If all the files are in a single folder and that folder contains no other items, navigate to that folder, then use `Ctrl + a` to select all the files in the folder.", validators=[DataRequired()])