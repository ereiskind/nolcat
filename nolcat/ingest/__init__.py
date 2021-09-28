from flask import Blueprint

bp = Blueprint('ingest', __name__)

from . import views