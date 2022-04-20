from flask import Blueprint

bp = Blueprint('view_vendors', __name__, template_folder='templates')

from . import views

#ToDo: Create `forms.py`