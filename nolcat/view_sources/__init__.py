from flask import Blueprint

bp = Blueprint('view_sources', __name__, template_folder='templates', url_prefix='/view_sources')

from . import views

#ToDo: Create `forms.py`