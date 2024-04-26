from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms.fields import MultipleFileField
from wtforms.fields import FieldList
from wtforms.fields import FormField
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


class HistoricalNonCOUNTERFormField(FlaskForm):
    """Creates a form field for uploading a file containing non-COUNTER usage data.
    
    This field is called iteratively in `HistoricalNonCOUNTERForm` to create a form. This iterative form setup is taken from https://stackoverflow.com/a/28378186.
    """
    usage_file = FileField("Select the file containing the usage statistics for the statistics source and fiscal year below:")


class HistoricalNonCOUNTERForm(FlaskForm):
    """Creates a form by iterating the `HistoricalNonCOUNTERFormField` field.
    
    This form is created through an iteration of the `HistoricalNonCOUNTERFormField` field for each statistics source and fiscal year combination calling for non-COUNTER usage data. This iterative form setup is taken from https://stackoverflow.com/a/28378186.
    """
    usage_files = FieldList(FormField(HistoricalNonCOUNTERFormField))