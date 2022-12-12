from flask import Blueprint

bp = Blueprint('annual_stats', __name__, template_folder='templates', url_prefix='/annual_stats')

from . import views

#ToDo: Create `forms.py`