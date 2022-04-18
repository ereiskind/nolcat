from flask import Blueprint

bp = Blueprint('annual_stats', __name__, template_folder='templates')

from . import views

#ToDo: Create `forms.py`