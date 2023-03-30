from flask import Blueprint

bp = Blueprint('login', __name__, template_folder='templates', url_prefix='/login')

from . import views
# from . import forms