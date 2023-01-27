from flask import Blueprint

bp = Blueprint('view_lists', __name__, template_folder='templates', url_prefix='/view_lists')

from . import views
from . import forms