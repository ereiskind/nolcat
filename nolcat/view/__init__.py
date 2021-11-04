from flask import Blueprint

bp = Blueprint('view', __name__, template_folder='templates')

from . import views