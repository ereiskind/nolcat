from flask import Blueprint

bp = Blueprint('login', __name__, template_folder='templates')

from . import views

#ToDo: Create `forms.py`