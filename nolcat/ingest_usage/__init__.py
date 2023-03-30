from flask import Blueprint

bp = Blueprint('ingest_usage', __name__, template_folder='templates', url_prefix='/ingest_usage')

from . import views
from . import forms