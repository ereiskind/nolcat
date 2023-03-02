from flask_wtf import FlaskForm
from wtforms.fields import SelectField
from wtforms.validators import InputRequired


class ChooseFiscalYearForm(FlaskForm):
    """Creates a form for choosing the fiscal year when viewing details about a fiscal year."""
    fiscal_year = SelectField("View the details for the fiscal year (fiscal years are represented by the year they end in):", coerce=int, validators=[InputRequired])


class RunAnnualStatsMethodsForm(FlaskForm):
    """Creates a form for running the annual usage statistics methods in the `FiscalYears` relation class."""
    annual_stats_method = SelectField(
        #ToDo: Create select field with choices
            # calculate_ACRL_60b()
            # calculate_ACRL_63()
            # calculate_ARL_18()
            # calculate_ARL_19()
            # calculate_ARL_20()
    )


class EditFiscalYearForm(FlaskForm):
    """Creates a form for editing records in the `fiscalYears` relation."""
    #ToDo: Create a field to edit `fiscal_year`
    #ToDo: Create a field to edit `start_date`
    #ToDo: Create a field to edit `end_date`
    #ToDo: Create a field to edit `ACRL_60b`
    #ToDo: Create a field to edit `ACRL_63`
    #ToDo: Create a field to edit `ARL_18`
    #ToDo: Create a field to edit `ARL_19`
    #ToDo: Create a field to edit `ARL_20`
    #ToDo: Create a field to edit `notes_on_statisticsSources_used`
    #ToDo: Create a field to edit `notes_on_corrections_after_submission`
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