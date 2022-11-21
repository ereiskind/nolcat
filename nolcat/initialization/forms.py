from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.file import FileRequired
from wtforms.fields import MultipleFileField
from wtforms.validators import DataRequired


class InitialRelationDataForm(FlaskForm):
    """Creates a form for uploading the non-usage database initialization data."""
    fiscalYears_TSV = FileField("Select the filled out \"initialize_fiscalYears.tsv\" file here.", validators=[DataRequired()])
    

class AUCTAndCOUNTERForm(FlaskForm):
    """Creates a form for uploading the `annualUsageCollectionTracking` relation data and the reformatted COUNTER R4 TSV files."""
    annualUsageCollectionTracking_TSV = FileField("Select the filled out \"initialize_annualUsageCollectionTracking.tsv\" file here.", validators=[FileRequired(), DataRequired()])
    COUNTER_TSVs = MultipleFileField("Select the reformatted R4 reports. If all the files are in a single folder and that folder contains no other items, navigate to that folder, then use `Ctrl + a` to select all the files in the folder.", validators=[DataRequired()])  # `FileRequired` validator on MultipleFileField causes `validate_on_submit()` to return false