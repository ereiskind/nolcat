from flask import Blueprint

bp = Blueprint('initialization', __name__, template_folder='templates')

from . import views

#ToDo: Create `forms.py`