from flask import Blueprint

bp = Blueprint('initialization', __name__, template_folder='templates', url_prefix='/initialization')

from . import views
from . import forms