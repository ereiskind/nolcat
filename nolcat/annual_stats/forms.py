from flask_wtf import FlaskForm
from wtforms.fields import SelectField
from wtforms.validators import InputRequired
from wtforms.validators import DataRequired


class ChooseFiscalYearForm(FlaskForm):
    """Creates a form for choosing the fiscal year when viewing details about a fiscal year."""
    fiscal_year = SelectField("View the details for the fiscal year (fiscal years are represented by the year they end in):", coerce=int, validators=[InputRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`


class RunAnnualStatsMethodsForm(FlaskForm):
    """Creates a form for running the annual usage statistics methods in the `FiscalYears` relation class."""
    #annual_stats_method = SelectField(#ToDo: Write label for field, choices=[
        # calculate_depreciated_ACRL_60b()
        # calculate_depreciated_ACRL_63()
        # calculate_ACRL_61a
        # calculate_ACRL_61b
        # calculate_ARL_18()
        # calculate_ARL_19()
        # calculate_ARL_20()
    #], validators=[DataRequired()], validate_choice=False)  # Without `validate_choice=False`, this field returns an error of `Not a valid choice`


class EditFiscalYearForm(FlaskForm):
    """Creates a form for editing records in the `fiscalYears` relation."""
    #ToDo: Create a field to edit `fiscal_year`
    #ToDo: Create a field to edit `start_date`
    #ToDo: Create a field to edit `end_date`
    #ToDo: Create a field to edit `notes_on_statisticsSources_used`
    #ToDo: Create a field to edit `notes_on_corrections_after_submission`
    pass


class EditAnnualStatisticsForm(FlaskForm):
    """Creates a form for adding records to the `annualStatistics` relation."""
    #ToDo: Create a field to select the fiscal year
    #ToDo: Create a field to enter the question
    #ToDo: Create a field to enter the value
    pass


class EditAUCTForm(FlaskForm):
    """Creates a form for editing records in the `annualUsageCollectionTracking` relation."""
    #ToDo: Create a field to edit `usage_is_being_collected`
    #ToDo: Create a field to edit `manual_collection_required`
    #ToDo: Create a field to edit `collection_via_email`
    #ToDo: Create a field to edit `is_COUNTER_compliant`
    #ToDo: Create a field to edit `collection_status`, which has the choices
        # 'N/A: Paid by Law',
        # 'N/A: Paid by Med',
        # 'N/A: Paid by Music',
        # 'N/A: Open access',
        # 'N/A: Other (see notes)',
        # 'Collection not started',
        # 'Collection in process (see notes)',
        # 'Collection issues requiring resolution',
        # 'Collection complete',
        # 'Usage not provided',
        # 'No usage to report'
    #ToDo: Create a field to edit `usage_file_path`
    #ToDo: Create a field to edit `notes`
    pass