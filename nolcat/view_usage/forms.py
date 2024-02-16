from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField
from wtforms.fields import SelectField
from wtforms.fields import DateField
from wtforms.fields import SelectMultipleField
from wtforms.fields import StringField
from wtforms.fields import IntegerField
from wtforms.fields import BooleanField
from wtforms.validators import DataRequired
from wtforms.validators import InputRequired
from wtforms.validators import Optional
from wtforms.validators import Regexp

from ..app import *


#Section: Report Attribute Lists
#Subsection: Variable Attribute Lists
# The keys are used in each form class to get only the possible valid values; to get all tuples for the drop-down, use the `.values()` iterator
data_type_values = {
    'Article': ('Article', "Article"),
    'Audiovisual': ('Audiovisual', "Audiovisual*"),
    'Book': ('Book', "Book"),
    'Book_Segment': ('Book_Segment', "Book Segment"),
    'Conference': ('Conference', "Conference*"),
    'Conference_Item': ('Conference_Item', "Conference Item*"),
    'Database_Aggregated': ('Database|Database_Aggregated', "Aggregated Database*"),
    'Database_AI': ('Database|Database_AI', "A&I Database*"),
    'Database_Full': ('Database|Database_Full', "Full Text Database*"),
    'Database': ('Database', "Database"),
    'Database_Full_Item': ('Database|Database_Full_Item', "Full Text Database Item*"),
    'Dataset': ('Dataset', "Dataset"),
    'Image': ('Image', "Image*"),
    'Interactive_Resource': ('Interactive_Resource', "Interactive Resource*"),
    'Journal': ('Journal', "Journal"),
    'Multimedia': ('Multimedia', "Multimedia"),
    'News_Item': ('News_Item', "News Item*"),
    'Newspaper_or_Newsletter': ('Newspaper_or_Newsletter', "Newspaper/Newsletter"),
    'Other': ('Other', "Other"),
    'Patent': ('Patent', "Patent*"),
    'Platform': ('Platform', "Platform"),
    'Reference_Item': ('Reference_Item', "Reference Item*"),
    'Reference_Work': ('Reference_Work', "Reference Work*"),
    'Report': ('Report', "Report"),
    'Repository_Item': ('Repository_Item', "Repository Item"),
    'Software': ('Software', "Software*"),
    'Sound': ('Sound', "Sound*"),
    'Standard': ('Standard', "Standard*"),
    'Thesis_or_Dissertation': ('Thesis_or_Dissertation', "Thesis/Dissertation"),
    'Unspecified': ('Unspecified', "Unspecified"),
}

metric_type_values = {
    'Searches_Regular': ('Searches_Regular|Regular Searches', "Database Searches"),
    'Searches_Automated': ('Searches_Automated|Searches-federated and automated|Searches: federated and automated', "Automated Database Searches"),
    'Searches_Federated': ('Searches_Federated|Searches-federated and automated|Searches: federated and automated', "Federated Database Searches"),
    'Searches_Platform': ('Searches_Platform|Regular Searches', "Platform Searches"),
    'Total_Item_Investigations': ('Total_Item_Investigations', "Total Item Investigations"),
    'Unique_Item_Investigations': ('Unique_Item_Investigations', "Unique Item Investigations"),
    'Unique_Title_Investigations': ('Unique_Title_Investigations', "Unique Title Investigations"),
    'Total_Item_Requests': ('Total_Item_Requests|Successful Full-text Article Requests|Successful Title Requests|Successful Section Requests|Successful Content Unit Requests', "Total Item Requests"),
    'Unique_Item_Requests': ('Unique_Item_Requests', "Unique Item Requests"),
    'Unique_Title_Requests': ('Unique_Title_Requests|Successful Title Requests', "Unique Title Requests"),
    'No_License': ('No_License|Access denied: content item not licensed', "Access Denied: No License"),
    'Limit_Exceeded': ('Limit_Exceeded|Access denied: concurrent/simultaneous user license limit exceeded|Access denied: concurrent/simultaneous user license exceeded. (Currently N/A to all platforms).', "Access Denied: User Limit Exceeded"),
}

#Subsection: Constant Attribute Lists
access_type_values = [
    ('Controlled', "Controlled"),
    ('OA_Gold|Open', "Open Access"),
    ('Other_Free_To_Read|Free_To_Read', "Free to Read"),
]
access_method_values = [
    ('Regular', "Regular"),
    ('TDM', "TDM"),
]


#Section: Form Classes
class CustomSQLQueryForm(FlaskForm):
    """Creates a form for entering a custom SQL query."""
    SQL_query = TextAreaField("Enter the SQL query:")
    open_in_Excel = BooleanField("Check if the CSV will be opened in Excel:")


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
    open_in_Excel = BooleanField("Check if the CSV will be opened in Excel:")


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
    begin_date = DateField("Enter the first day of the first month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField("Enter the last day of the last month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[DataRequired()])
    display_fields = SelectMultipleField("Select the fields the query should return:", choices=[
        ('platform', "Platform"),
        ('data_type', "Data Type"),
        ('access_method', "Access Method"),
    ], validators=[Optional()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
    platform_filter = StringField("Enter the name of the platform the query should return:", validators=[Optional()])
    data_type_filter = SelectMultipleField("Select all of the data types the query should return (all data types ending in asterisks have yet to be implemented):", choices=[
        data_type_values['Article'],
        data_type_values['Audiovisual'],
        data_type_values['Book'],
        data_type_values['Book_Segment'],
        data_type_values['Conference'],
        data_type_values['Conference_Item'],
        data_type_values['Database'],
        data_type_values['Database_Full_Item'],
        data_type_values['Dataset'],
        data_type_values['Image'],
        data_type_values['Interactive_Resource'],
        data_type_values['Journal'],
        data_type_values['Multimedia'],
        data_type_values['News_Item'],
        data_type_values['Newspaper_or_Newsletter'],
        data_type_values['Other'],
        data_type_values['Patent'],
        data_type_values['Platform'],
        data_type_values['Reference_Item'],
        data_type_values['Reference_Work'],
        data_type_values['Report'],
        data_type_values['Repository_Item'],
        data_type_values['Software'],
        data_type_values['Sound'],
        data_type_values['Standard'],
        data_type_values['Thesis_or_Dissertation'],
        data_type_values['Unspecified'],
    ], validators=[Optional()])
    access_method_filter = SelectMultipleField("Select all of the access methods the query should return:", choices=access_method_values, validators=[Optional()])
    metric_type_filter = SelectMultipleField("Select all of the metric types the query should return:", choices=[
        metric_type_values['Searches_Platform'],
        metric_type_values['Total_Item_Investigations'],
        metric_type_values['Unique_Item_Investigations'],
        metric_type_values['Unique_Title_Investigations'],
        metric_type_values['Total_Item_Requests'],
        metric_type_values['Unique_Item_Requests'],
        metric_type_values['Unique_Title_Requests'],
    ], validators=[Optional()])
    open_in_Excel = BooleanField("Check if the CSV will be opened in Excel:")


class DRQueryWizardForm(FlaskForm):
    """Creates a form for selecting the fields and creating the filters for querying the `COUNTERData` relation for database data."""
    begin_date = DateField("Enter the first day of the first month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField("Enter the last day of the last month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[DataRequired()])
    display_fields = SelectMultipleField("Select the fields the query should return:", choices=[
        ('resource_name', "Database Name"),
        ('publisher', "Publisher"),
        ('platform', "Platform"),
        ('data_type', "Data Type"),
        ('access_method', "Access Method"),
    ], validators=[Optional()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
    resource_name_filter = StringField("Enter the name of the database the query should return:", validators=[Optional()])
    publisher_filter = StringField("Enter the name of the publisher the query should return:", validators=[Optional()])
    platform_filter = StringField("Enter the name of the platform the query should return:", validators=[Optional()])
    data_type_filter = SelectMultipleField("Select all of the data types the query should return (all data types ending in asterisks have yet to be implemented):", choices=[
        data_type_values['Audiovisual'],
        data_type_values['Book'],
        data_type_values['Conference'],
        data_type_values['Database_Aggregated'],
        data_type_values['Database_AI'],
        data_type_values['Database_Full'],
        data_type_values['Database'],
        data_type_values['Database_Full_Item'],
        data_type_values['Image'],
        data_type_values['Interactive_Resource'],
        data_type_values['Journal'],
        data_type_values['Multimedia'],
        data_type_values['Newspaper_or_Newsletter'],
        data_type_values['Other'],
        data_type_values['Patent'],
        data_type_values['Reference_Work'],
        data_type_values['Report'],
        data_type_values['Sound'],
        data_type_values['Standard'],
        data_type_values['Thesis_or_Dissertation'],
        data_type_values['Unspecified'],
    ], validators=[Optional()])
    access_method_filter = SelectMultipleField("Select all of the access methods the query should return:", choices=access_method_values, validators=[Optional()])
    metric_type_filter = SelectMultipleField("Select all of the metric types the query should return:", choices=[
        metric_type_values['Searches_Regular'],
        metric_type_values['Searches_Automated'],
        metric_type_values['Searches_Federated'],
        metric_type_values['Total_Item_Investigations'],
        metric_type_values['Unique_Item_Investigations'],
        metric_type_values['Unique_Title_Investigations'],
        metric_type_values['Total_Item_Requests'],
        metric_type_values['Unique_Item_Requests'],
        metric_type_values['Unique_Title_Requests'],
        metric_type_values['No_License'],
        metric_type_values['Limit_Exceeded'],
    ], validators=[Optional()])
    open_in_Excel = BooleanField("Check if the CSV will be opened in Excel:")


class TRQueryWizardForm(FlaskForm):
    """Creates a form for selecting the fields and creating the filters for querying the `COUNTERData` relation for title data."""
    begin_date = DateField("Enter the first day of the first month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField("Enter the last day of the last month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[DataRequired()])
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
        ('access_type', "Access Type"),
        ('access_method', "Access Method"),
    ], validators=[Optional()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
    resource_name_filter = StringField("Enter the name of the title-level resource the query should return:", validators=[Optional()])
    publisher_filter = StringField("Enter the name of the publisher the query should return:", validators=[Optional()])
    platform_filter = StringField("Enter the name of the platform the query should return:", validators=[Optional()])
    ISBN_filter = StringField("Enter the ISBN of the title the query should return:", validators=[Optional(), Regexp(ISBN_regex())])
    ISSN_filter = StringField("Enter the ISSN of the title the query should return:", validators=[Optional(), Regexp(ISSN_regex())])
    data_type_filter = SelectMultipleField("Select all of the data types the query should return (all data types ending in asterisks have yet to be implemented):", choices=[
        data_type_values['Book'],
        data_type_values['Conference'],
        data_type_values['Journal'],
        data_type_values['Newspaper_or_Newsletter'],
        data_type_values['Other'],
        data_type_values['Patent'],
        data_type_values['Reference_Work'],
        data_type_values['Report'],
        data_type_values['Standard'],
        data_type_values['Thesis_or_Dissertation'],
        data_type_values['Unspecified'],
    ], validators=[Optional()])
    section_type_filter = SelectMultipleField("Select all of the section types the query should return (this field is only used in COUNTER R5.0):", choices=[
        ('Article', "Article"),
        ('Book', "Book"),
        ('Chapter', "Chapter"),
        ('Other', "Other"),
        ('Section', "Section"),
    ], validators=[Optional()])
    YOP_start_filter = IntegerField("Enter the earliest year of publication the query should return:", validators=[Optional()])
    YOP_end_filter = IntegerField("Enter the latest year of publication the query should return (if this is before the previous value, this filter won't be used):", validators=[Optional()])
    access_type_filter = SelectMultipleField("Select all of the access types the query should return:", choices=access_type_values, validators=[Optional()])
    access_method_filter = SelectMultipleField("Select all of the access methods the query should return:", choices=access_method_values, validators=[Optional()])
    metric_type_filter = SelectMultipleField("Select all of the metric types the query should return:", choices=[
        metric_type_values['Total_Item_Investigations'],
        metric_type_values['Unique_Item_Investigations'],
        metric_type_values['Unique_Title_Investigations'],
        metric_type_values['Total_Item_Requests'],
        metric_type_values['Unique_Item_Requests'],
        metric_type_values['Unique_Title_Requests'],
        metric_type_values['No_License'],
        metric_type_values['Limit_Exceeded'],
    ], validators=[Optional()])
    open_in_Excel = BooleanField("Check if the CSV will be opened in Excel:")


class IRQueryWizardForm(FlaskForm):
    """Creates a form for selecting the fields and creating the filters for querying the `COUNTERData` relation for item data."""
    begin_date = DateField("Enter the first day of the first month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField("Enter the last day of the last month for which usage should be collected in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[DataRequired()])
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
        ('access_type', "Access Type"),
        ('access_method', "Access Method"),
    ], validators=[Optional()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
    resource_name_filter = StringField("Enter the name of the item-level resource the query should return:", validators=[Optional()])
    publisher_filter = StringField("Enter the name of the publisher the query should return:", validators=[Optional()])
    platform_filter = StringField("Enter the name of the platform the query should return:", validators=[Optional()])
    publication_date_start_filter = DateField("Enter the earliest publication date of the items the query should return in 'yyyy-mm-dd' format:", format='%Y-%m-%d', validators=[Optional()])
    publication_date_end_filter = DateField("Enter the latest publication date of the items the query should return in 'yyyy-mm-dd' format (if this is before the previous value, this filter won't be used):", format='%Y-%m-%d', validators=[Optional()])
    ISBN_filter = StringField("Enter the ISBN of the item the query should return:", validators=[Optional(), Regexp(ISBN_regex())])
    ISSN_filter = StringField("Enter the ISSN of the item the query should return:", validators=[Optional(), Regexp(ISSN_regex())])
    parent_title_filter = StringField("Enter the name of the parent of the item-level resources the query should return:", validators=[Optional()])
    parent_ISBN_filter = StringField("Enter the ISBN of the parent of the item the query should return:", validators=[Optional(), Regexp(ISBN_regex())])
    parent_ISSN_filter = StringField("Enter the ISSN of the parent of the item the query should return:", validators=[Optional(), Regexp(ISSN_regex())])
    data_type_filter = SelectMultipleField("Select all of the data types the query should return (all data types ending in asterisks have yet to be implemented):", choices=[
        data_type_values['Article'],
        data_type_values['Audiovisual'],
        data_type_values['Book'],
        data_type_values['Book_Segment'],
        data_type_values['Conference_Item'],
        data_type_values['Database_Full_Item'],
        data_type_values['Dataset'],
        data_type_values['Image'],
        data_type_values['Interactive_Resource'],
        data_type_values['Journal'],
        data_type_values['Multimedia'],
        data_type_values['News_Item'],
        data_type_values['Newspaper_or_Newsletter'],
        data_type_values['Other'],
        data_type_values['Patent'],
        data_type_values['Reference_Item'],
        data_type_values['Report'],
        data_type_values['Repository_Item'],
        data_type_values['Software'],
        data_type_values['Sound'],
        data_type_values['Standard'],
        data_type_values['Thesis_or_Dissertation'],
        data_type_values['Unspecified'],
    ], validators=[Optional()])
    YOP_start_filter = IntegerField("Enter the earliest year of publication the query should return:", validators=[Optional()])
    YOP_end_filter = IntegerField("Enter the latest year of publication the query should return (if this is before the previous value, this filter won't be used):", validators=[Optional()])
    access_type_filter = SelectMultipleField("Select all of the access types the query should return:", choices=access_type_values, validators=[Optional()])
    access_method_filter = SelectMultipleField("Select all of the access methods the query should return:", choices=access_method_values, validators=[Optional()])
    metric_type_filter = SelectMultipleField("Select all of the metric types the query should return:", choices=[
        metric_type_values['Total_Item_Investigations'],
        metric_type_values['Unique_Item_Investigations'],
        metric_type_values['Total_Item_Requests'],
        metric_type_values['Unique_Item_Requests'],
        metric_type_values['No_License'],
        metric_type_values['Limit_Exceeded'],
    ], validators=[Optional()])
    open_in_Excel = BooleanField("Check if the CSV will be opened in Excel:")


class ChooseNonCOUNTERDownloadForm(FlaskForm):
    """Creates a form allowing the download of all saved non-COUNTER usage files."""
    AUCT_of_file_download = SelectField("Choose the usage statistics file to download:", validators=[InputRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`
