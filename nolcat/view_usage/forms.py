from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField


class CustomSQLQueryForm(FlaskForm):
    """Creates a form for entering a custom SQL query."""
    SQL_query = TextAreaField("Enter the SQL query:")