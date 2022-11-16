from flask import Blueprint

bp = Blueprint('view_resources', __name__, template_folder='templates', url_prefix='/view_resources')

from . import views

#ToDo: Create `forms.py`