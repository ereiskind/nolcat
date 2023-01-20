from flask import Blueprint

bp = Blueprint('view_usage', __name__, template_folder='templates', url_prefix='/view_usage')

from . import views

#ToDo: Create `forms.py`