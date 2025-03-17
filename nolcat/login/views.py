import logging
from flask import render_template

from . import bp
#from .forms import *
from ..app import *
from ..models import *
from ..statements import *

log = logging.getLogger(__name__)
#ToDo: Testing based on https://www.edstem.com/blog/orchestrating-async-workflows-aws/


def call_lambda(name_of_lambda_function, payload):
    lambda_client = boto3.client("lambda")
    lambda_client.invoke(
        FunctionName=name_of_lambda_function,
        InvocationType="Event",  # "Invoke the function asynchronously. Send events that fail multiple times to the function’s dead-letter queue (if one is configured). The API response only includes a status code."
        Payload=payload  # "The JSON that you want to provide to your Lambda function as input."
    )
    return None


@bp.route('/')
def login_homepage():
    """Returns the homepage for the `login` blueprint."""
    # log.info("Starting `login_homepage()`.")
    #ToDo: Should this be the page for logging in (entering existing credentials) with Flask-User?
    return render_template('login/index.html')


#ToDo: If individual accounts are to be used, create route to account creation page with Flask-User