from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField

class TestForm(FlaskForm):
    checkbox = BooleanField("A checkbox")
    submit_button = SubmitField("The submit button")