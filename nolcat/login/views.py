import logging
from flask import render_template
#TEST: temp
from flask import request
from flask import redirect
from flask import url_for
from flask import abort
from flask import flash
#TEST: end temp

from . import bp
from .forms import *
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


@bp.route('/', methods=['GET', 'POST'])  #TEST: methods are temp
def login_homepage():
    """Returns the homepage for the `login` blueprint."""
    # log.info("Starting `login_homepage()`.")
    #ToDo: Should this be the page for logging in (entering existing credentials) with Flask-User?
    #TEST: temp `return render_template('login/index.html')`
    form = TestForm()
    if request.method == 'GET':
        return render_template('login/index.html', form=form)
    elif form.validate_on_submit():
        Bool_data = form.Bool_data.data  # [2025-03-18 15:44:48] nolcat.login.views::42 - `Bool_data` (type <class 'bool'>): True
        int_data = form.int_data.data  # [2025-03-18 15:44:48] nolcat.login.views::44 - `int_data` (type <class 'int'>): 2
        string_data = form.string_data.data  # [2025-03-18 15:44:48] nolcat.login.views::46 - `string_data` (type <class 'str'>): df
        date_data = form.date_data.data  # [2025-03-18 15:44:48] nolcat.login.views::48 - `date_data` (type <class 'datetime.date'>): 2025-02-25
        select_data = form.select_data.data  # [2025-03-18 15:44:48] nolcat.login.views::50 - `select_data` (type <class 'str'>): 1
        #file_data = form.file_data.data
        #log.warning(f"`file_data` (type {type(file_data)}): {file_data}")
        text_data = form.text_data.data  # [2025-03-18 15:44:48] nolcat.login.views::54 - `text_data` (type <class 'str'>): 2222222222222
        multiple_select_data = form.multiple_select_data.data  # [2025-03-18 15:44:48] nolcat.login.views::56 - `multiple_select_data` (type <class 'list'>): ['a', 'c']
        multiple_file_data = form.multiple_file_data.data  # [2025-03-18 15:44:48] nolcat.login.views::58 - `multiple_file_data` (type <class 'list'>): ['hello_world.json', 'hello_world.py']
        log.warning(f"`multiple_file_data[0]` (type {type(multiple_file_data[0])}): {multiple_file_data[0]}")

        payload = request.get_json()
        log.warning(f"`payload` (type {type(payload)}):\n{payload}")
        lambda_name = "test_lambda_function"
        call_lambda(lambda_name, json.dumps(payload))  # `json.dumps()` is for JSON -> str, so second arg of `call_lambda()` is string
        return "Workflow triggered"
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)


#ToDo: If individual accounts are to be used, create route to account creation page with Flask-User