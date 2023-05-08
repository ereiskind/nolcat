from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField
from wtforms.fields import SelectField
from wtforms.fields import DateField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired


class CustomSQLQueryForm(FlaskForm):
    """Creates a form for entering a custom SQL query."""
    SQL_query = TextAreaField("Enter the SQL query:")


class QueryWizardForm(FlaskForm):
    """Creates a form that serves as a wizard for querying the NoLCAT database."""
    begin_date = DateField("Enter the first day of the first month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField("Enter the last day of the last month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[DataRequired()])
    query_options = SelectField("Select the type of report you want:", choices=[
        ('PR_P1', "PR_P1"),
        ('DR_D1', ""),
        ('DR_D2', ""),
        ('TR_B1', ""),
        ('TR_B2', ""),
        ('TR_B3', ""),
        ('TR_J1', ""),
        ('TR_J2', ""),
        ('TR_J3', ""),
        ('TR_J4', ""),
        ('IR_A1', ""),
        ('IR_M1', ""),
        ('w', "Create a query with the wizard options below:")
    ], validators=[DataRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
    #ToDo: Add wizard option fields


class ChooseNonCOUNTERDownloadForm(FlaskForm):
    """Creates a form allowing the download of all saved non-COUNTER usage files."""
    file_download = SelectField("Choose the usage statistics file to download:", validators=[InputRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`