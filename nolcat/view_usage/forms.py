from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField
from wtforms.fields import SelectField
from wtforms.fields import DateField
from wtforms.fields import SelectMultipleField
from wtforms.fields import StringField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired
from wtforms.validators import Optional


data_type_values = ['Article', 'Audiovisual', 'Book', 'Book_Segment', 'Conference', 'Conference_Item', 'Database_Aggregated', 'Database_AI', 'Database_Full', 'Database_Full_Item', 'Dataset', 'Image', 'Interactive_Resource', 'Journal', 'Multimedia', 'News_Item', 'Newspaper_or_Newsletter', 'Other', 'Patent', 'Platform', 'Reference_Item', 'Reference_Work', 'Report', 'Software', 'Sound', 'Standard', 'Thesis_or_Dissertation', 'Unspecified']
metric_type_values = ['Searches_Regular', 'Searches_Automated', 'Searches_Federated', 'Searches_Platform', 'Total_Item_Investigations', 'Unique_Item_Investigations', 'Unique_Title_Investigations', 'Total_Item_Requests', 'Unique_Item_Requests', 'Unique_Title_Requests', 'No_License', 'Limit_Exceeded']
access_type_values = ['Controlled', 'Open', 'Free_To_Read']
access_method_values = ['Regular', 'TDM']


class CustomSQLQueryForm(FlaskForm):
    """Creates a form for entering a custom SQL query."""
    SQL_query = TextAreaField("Enter the SQL query:")


class PresetQueryForm(FlaskForm):
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


class StartQueryWizardForm(FlaskForm):
    """Creates a form that collects the start date, end date, and report type for a query constructed with the wizard."""
    begin_date = DateField("Enter the first day of the first month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField("Enter the last day of the last month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[Optional()])
    fiscal_year = SelectField("Select the fiscal year for which usage should be collected:", coerce=int, validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
    report_type = SelectField("Select the type of report you want:", choices=[
        ('PR', "PR"),
        ('DR', "DR"),
        ('TR', "TR"),
        ('IR', "IR"),
    ], validators=[DataRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`


class PRQueryWizardForm(FlaskForm):
    """Creates a form for selecting the fields and creating the filters for querying the `COUNTERData` relation for platform data."""
    display_fields = SelectMultipleField("Select the fields the query should return:", choices=[
        ('platform', "Platform"),
        ('data_type', "Data Type"),
        ('access_method', "Access Method"),
    ], validators=[DataRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
    platform_filter = StringField("Enter the name of the platform the query should return:", validators=[Optional()])
    data_type_filter = SelectMultipleField("Select all of the data types the query should return:", choices=data_type_values)  #ToDo: Should all values be leaving this blank?
    access_method_filter = SelectMultipleField("Select all of the access methods the query should return:", choices=access_method_values)  #ToDo: Should all values be leaving this blank?
    metric_type_filter = SelectMultipleField("Select all of the metric types the query should return:", choices=metric_type_values)  #ToDo: Should all values be leaving this blank?


class DRQueryWizardForm(FlaskForm):
    """Creates a form for selecting the fields and creating the filters for querying the `COUNTERData` relation for database data."""
    display_fields = SelectMultipleField("Select the fields the query should return:", choices=[
        ('resource_name', "Database Name"),
        ('publisher', "Publisher"),
        ('platform', "Platform"),
        ('data_type', "Data Type"),
        ('access_method', "Access Method"),
    ], validators=[DataRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
    resource_name_filter = StringField("Enter the name of the database the query should return:", validators=[Optional()])
    publisher_filter = StringField("Enter the name of the publisher the query should return:", validators=[Optional()])
    platform_filter = StringField("Enter the name of the platform the query should return:", validators=[Optional()])
    data_type_filter = SelectMultipleField("Select all of the data types the query should return:", choices=data_type_values)  #ToDo: Should all values be leaving this blank?
    access_method_filter = SelectMultipleField("Select all of the access methods the query should return:", choices=access_method_values)  #ToDo: Should all values be leaving this blank?
    metric_type_filter = SelectMultipleField("Select all of the metric types the query should return:", choices=metric_type_values)  #ToDo: Should all values be leaving this blank?


class TRQueryWizardForm(FlaskForm):
    """Creates a form for selecting the fields and creating the filters for querying the `COUNTERData` relation for title data."""
    display_fields = SelectMultipleField("Select the fields the query should return:", choices=[
        ('resource_name', "Title Name"),
        ('publisher', "Publisher"),
        ('platform', "Platform"),
        ('DOI', "DOI"),
        ('ISBN', "ISBN"),
        ('print_ISSN', "Print ISSN"),
        ('online_ISSN', "Online ISSN"),
        ('data_type', "Data Type"),
        ('section_type', "Section Type"),
        ('YOP', "Year of Publication"),
        ('access_method', "Access Method"),
    ], validators=[DataRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
    resource_name_filter = StringField("Enter the name of the title-level resource the query should return:", validators=[Optional()])
    publisher_filter = StringField("Enter the name of the publisher the query should return:", validators=[Optional()])
    platform_filter = StringField("Enter the name of the platform the query should return:", validators=[Optional()])
    ISBN_filter = StringField("Enter the ISBN of the title the query should return:", validators=[Optional()])
    ISSN_filter = StringField("Enter the ISSN of the title the query should return:", validators=[Optional()])
    data_type_filter = SelectMultipleField("Select all of the data types the query should return:", choices=data_type_values)  #ToDo: Should all values be leaving this blank?
    section_type_filter = SelectMultipleField("Select all of the section types the query should return:", choices=data_type_values)  #ToDo: Should all values be leaving this blank?
    YOP_filter = IntegerRangeField("Select the range for the year of publication of the title the query should return:", validators=[Optional()])  #ToDo: Should all values be leaving this blank?
    access_type_filter = SelectMultipleField("Select all of the access types the query should return:", choices=access_type_values)  #ToDo: Should all values be leaving this blank?
    access_method_filter = SelectMultipleField("Select all of the access methods the query should return:", choices=access_method_values)  #ToDo: Should all values be leaving this blank?
    metric_type_filter = SelectMultipleField("Select all of the metric types the query should return:", choices=metric_type_values)  #ToDo: Should all values be leaving this blank?


class IRQueryWizardForm(FlaskForm):
    """Creates a form for selecting the fields and creating the filters for querying the `COUNTERData` relation for item data."""
    display_fields = SelectMultipleField("Select the fields the query should return:", choices=[
        ('resource_name', "Item Name"),
        ('publisher', "Publisher"),
        ('platform', "Platform"),
        ('publication_date', "Publication Date"),
        ('DOI', "DOI"),
        ('ISBN', "ISBN"),
        ('print_ISSN', "Print ISSN"),
        ('online_ISSN', "Online ISSN"),
        ('parent_title', "Parent Title"),
        ('parent_publication_date', "Parent Publication Date"),
        ('parent_data_type', "Parent Data Type"),
        ('parent_DOI', "Parent DOI"),
        ('parent_ISBN', "Parent ISBN"),
        ('parent_print_ISSN', "Parent Print ISSN"),
        ('parent_online_ISSN', "Parent Online ISSN"),
        ('data_type', "Data Type"),
        ('YOP', "Year of Publication"),
        ('access_method', "Access Method"),
    ], validators=[DataRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
    resource_name_filter = StringField("Enter the name of the item-level resource the query should return:", validators=[Optional()])
    publisher_filter = StringField("Enter the name of the publisher the query should return:", validators=[Optional()])
    platform_filter = StringField("Enter the name of the platform the query should return:", validators=[Optional()])
    publication_date_start_filter = DateField("Enter the earliest publication date of the items the query should return:", validators=[Optional()])
    publication_date_end_filter = DateField("Enter the latest publication date of the items the query should return:", validators=[Optional()])
    ISBN_filter = StringField("Enter the ISBN of the item the query should return:", validators=[Optional()])
    ISSN_filter = StringField("Enter the ISSN of the item the query should return:", validators=[Optional()])
    parent_title_filter = StringField("Enter the name of the parent of the item-level resources the query should return:", validators=[Optional()])
    ISBN_filter = StringField("Enter the ISBN of the parent of the item the query should return:", validators=[Optional()])
    ISSN_filter = StringField("Enter the ISSN of the parent of the item the query should return:", validators=[Optional()])
    data_type_filter = SelectMultipleField("Select all of the data types the query should return:", choices=data_type_values)  #ToDo: Should all values be leaving this blank?
    YOP_filter = IntegerRangeField("Select the range for the year of publication of the item the query should return:", validators=[Optional()])  #ToDo: Should all values be leaving this blank?
    access_type_filter = SelectMultipleField("Select all of the access types the query should return:", choices=access_type_values)  #ToDo: Should all values be leaving this blank?
    access_method_filter = SelectMultipleField("Select all of the access methods the query should return:", choices=access_method_values)  #ToDo: Should all values be leaving this blank?
    metric_type_filter = SelectMultipleField("Select all of the metric types the query should return:", choices=metric_type_values)  #ToDo: Should all values be leaving this blank?


class ChooseNonCOUNTERDownloadForm(FlaskForm):
    """Creates a form allowing the download of all saved non-COUNTER usage files."""
    AUCT_of_file_download = SelectField("Choose the usage statistics file to download:", validators=[InputRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`