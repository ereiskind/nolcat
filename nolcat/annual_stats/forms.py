from flask_wtf import FlaskForm
from wtforms.fields import SelectField


class ChooseFiscalYearForm(FlaskForm):
    """Creates a form for choosing the fiscal year when viewing details about a fiscal year."""
    fiscal_year = SelectField("View the details for the fiscal year (fiscal years are represented by the year they end in):", coerce=int)