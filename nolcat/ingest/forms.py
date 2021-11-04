from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class TestForm(FlaskForm):
    string = StringField('This is a string submission field')