from flask import Blueprint

bp = Blueprint('ingest', __name__, template_folder='templates')

from . import views