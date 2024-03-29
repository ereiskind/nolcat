from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms.fields import MultipleFileField
from wtforms.validators import DataRequired


class FYAndVendorsDataForm(FlaskForm):
    """Creates a form for uploading the `fiscalYears`, `annualStatistics`, `vendors`, and `vendorNotes` relation data."""
    fiscalYears_CSV = FileField("Select the filled out \"initialize_fiscalYears.csv\" file here.", validators=[DataRequired()])
    annualStatistics_CSV = FileField("Select the filled out \"initialize_annualStatistics.csv\" file here.", validators=[DataRequired()])
    vendors_CSV = FileField("Select the filled out \"initialize_vendors.csv\" file here.", validators=[DataRequired()])
    vendorNotes_CSV = FileField("Select the filled out \"initialize_vendorNotes.csv\" file here.", validators=[DataRequired()])


class SourcesDataForm(FlaskForm):
    """Creates a form for uploading the `statisticsSources`, `statisticsSourceNotes`, `resourceSources`, `resourceSourceNotes`, and `statisticsResourceSources` relation data."""
    statisticsSources_CSV = FileField("Select the filled out \"initialize_statisticsSources.csv\" file here.", validators=[DataRequired()])
    statisticsSourceNotes_CSV = FileField("Select the filled out \"initialize_statisticsSourceNotes.csv\" file here.", validators=[DataRequired()])
    resourceSources_CSV = FileField("Select the filled out \"initialize_resourceSources.csv\" file here.", validators=[DataRequired()])
    resourceSourceNotes_CSV = FileField("Select the filled out \"initialize_resourceSourceNotes.csv\" file here.", validators=[DataRequired()])
    statisticsResourceSources_CSV = FileField("Select the filled out \"initialize_statisticsResourceSources.csv\" file here.", validators=[DataRequired()])


class AUCTAndCOUNTERForm(FlaskForm):
    """Creates a form for uploading the `annualUsageCollectionTracking` relation data and Excel workbooks containing COUNTER reports."""
    annualUsageCollectionTracking_CSV = FileField("Select the filled out \"initialize_annualUsageCollectionTracking.csv\" file here.", validators=[DataRequired()])
    COUNTER_reports = MultipleFileField("Select the COUNTER report workbooks. If all the files are in a single folder and that folder contains no other items, navigate to that folder, then use `Ctrl + a` to select all the files in the folder.")