from flask_wtf import FlaskForm
#TEST: temp
from wtforms.fields import BooleanField
from wtforms.fields import IntegerField
from wtforms.fields import StringField
from wtforms.fields import DateField
from wtforms.fields import SelectField
from flask_wtf.file import FileField
from wtforms.fields import TextAreaField
from wtforms.fields import SelectMultipleField
from wtforms.fields import MultipleFileField
from wtforms.validators import DataRequired


class TestForm(FlaskForm):
    Bool_data = BooleanField("Check if the Boolean field value should be yes:")
    int_data = IntegerField("Enter a number for the integer field value:", validators=[DataRequired()])
    string_data = StringField("Enter a string for the string field value:", validators=[DataRequired()])
    date_data = DateField("Enter a date in 'yyyy-mm-dd' format for the date field value:", format='%Y-%m-%d', validators=[DataRequired()])
    select_data = SelectField("Select an option for the select field value:", choices=[
        (1, "Display One"),
        (2, "Display Two"),
        (3, "Display Three"),
    ], validate_choice=False)
    file_data = FileField("Select a file for the file field value:", validators=[DataRequired()])
    text_data = TextAreaField("Enter text for the text area field value:", validators=[DataRequired()])
    multiple_select_data = SelectMultipleField("Select multiple options for the select multiple field value:", choices=[
        ('a', "Display A"),
        ('b', "Display B"),
        ('c', "Display C"),
        ('d', "Display D"),
        ('e', "Display E"),
        ('f', "Display F"),
        ('g', "Display G"),
    ], validate_choice=False)
    multiple_file_data = MultipleFileField("Select multiple files for the multiple file field value:", validators=[DataRequired()])
#TEST: end temp