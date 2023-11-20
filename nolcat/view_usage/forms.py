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
        ('DR_D1', "DR_D1"),
        ('DR_D2', "DR_D2"),
        ('TR_B1', "TR_B1"),
        ('TR_B2', "TR_B2"),
        ('TR_B3', "TR_B3"),
        ('TR_J1', "TR_J1"),
        ('TR_J2', "TR_J2"),
        ('TR_J3', "TR_J3"),
        ('TR_J4', "TR_J4"),
        ('IR_A1', "IR_A1"),
        ('IR_M1', "IR_M1"),
    ], validators=[DataRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
'''
    SELECT
    <fields selected to display>,
        COUNTERData.resource_name
        COUNTERData.publisher
        COUNTERData.platform
        COUNTERData.publication_date
        COUNTERData.DOI
        COUNTERData.ISBN
        COUNTERData.print_ISSN
        COUNTERData.online_ISSN
        COUNTERData.data_type
        COUNTERData.section_type
        COUNTERData.YOP
        COUNTERData.access_method
        COUNTERData.parent_title
        COUNTERData.parent_publication_date
        COUNTERData.parent_data_type
        COUNTERData.parent_DOI
        COUNTERData.parent_ISBN
        COUNTERData.parent_print_ISSN
        COUNTERData.parent_online_ISSN
    COUNTERData.usage_date
    SUM(COUNTERData.usage_count)
FROM COUNTERData
WHERE
    COUNTERData.report_type -- PAGE 1
    COUNTERData.usage_date x2 -- PAGE 1
    <filter statements>
        COUNTERData.resource_name (needs fuzzy search)
        COUNTERData.publisher (less fuzzy search)
        COUNTERData.platform (less fuzzy search)
        COUNTERData.ISBN
        COUNTERData.print_ISSN OR COUNTERData.online_ISSN
        COUNTERData.publication_date
        COUNTERData.data_type
        COUNTERData.section_type
        COUNTERData.YOP
        COUNTERData.access_type
        COUNTERData.access_method
        COUNTERData.parent_title (needs fuzzy search)
        COUNTERData.parent_ISBN
        COUNTERData.parent_print_ISSN OR COUNTERData.parent_online_ISSN
GROUP BY
    <fields in select not in where or with a grouping function);
'''


class ChooseNonCOUNTERDownloadForm(FlaskForm):
    """Creates a form allowing the download of all saved non-COUNTER usage files."""
    AUCT_of_file_download = SelectField("Choose the usage statistics file to download:", validators=[InputRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`