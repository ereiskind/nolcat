from flask_wtf import FlaskForm
from wtforms.fields import SelectField
from wtforms.fields import DateField
from wtforms.fields import MultipleFileField
from wtforms.fields import FileField
from wtforms.validators import DataRequired
import pandas as pd


class COUNTERReportsForm(FlaskForm):
    """Creates a form for uploading Excel workbooks containing COUNTER reports."""
    COUNTER_reports = MultipleFileField("Select the COUNTER report workbooks. If all the files are in a single folder and that folder contains no other items, navigate to that folder, then use `Ctrl + a` to select all the files in the folder.", validators=[DataRequired()])


class SUSHIParametersForm(FlaskForm):
    """Creates a form for capturing the parameters for calling the `StatisticsSources.collect_usage_statistics()` method."""
    statistics_source = SelectField("pick stats source", coerce=int)
    begin_date = DateField("Beginning of timespan", validators=[DataRequired()])
    end_date = DateField("end of timespan", validators=[DataRequired()])  #ToDo: Check `view_usage` routes for handling validation of date sequence and last date of month


class UsageFileForm(FlaskForm):
    """Creates a form for selecting a given statistics source and fiscal year combination and uploading a file containing non-COUNTER usage data for that selection."""
    AUCT_option = SelectField("Select the statistics source and fiscal year for the usage data to be uploaded.", coerce=int)
    usage_file = FileField("Select the file containing the usage statistics for the statistics source and fiscal year stated above.", validators=[DataRequired()])