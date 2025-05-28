import logging
from flask import render_template
#TEST: temp
from flask import request
from flask import abort
from flask import flash
#TEST: end temp

from . import bp
from .forms import *
from ..app import *
from ..models import *
from ..statements import *

log = logging.getLogger(__name__)


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
        file_data = form.file_data.data  # [2025-03-18 20:36:41] nolcat.login.views::46 - `file_data` (type <class 'werkzeug.datastructures.file_storage.FileStorage'>): <FileStorage: '58_2020.xlsx' ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')>
        text_data = form.text_data.data  # [2025-03-18 15:44:48] nolcat.login.views::54 - `text_data` (type <class 'str'>): 2222222222222
        multiple_select_data = form.multiple_select_data.data  # [2025-03-18 15:44:48] nolcat.login.views::56 - `multiple_select_data` (type <class 'list'>): ['a', 'c']
        multiple_file_data = form.multiple_file_data.data  # [2025-03-18 15:44:48] nolcat.login.views::58 - `multiple_file_data` (type <class 'list'>): ['hello_world.json', 'hello_world.py']
        # [2025-03-18 16:05:24] nolcat.login.views::51 - `multiple_file_data[0]` (type <class 'werkzeug.datastructures.file_storage.FileStorage'>): <FileStorage: '391_Oct 2022-Jun 2023.xlsx' ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')>

        # [2025-03-18 16:05:24] nolcat.login.views::53 - `request` (type <class 'werkzeug.local.LocalProxy'>): <Request 'http://nolcat:5000/login/' [POST]>
        '''
        {
            'method': 'POST',
            'scheme': 'http',
            'server': ('0.0.0.0', 5000),
            'root_path': '',
            'path': '/login/',
            'query_string': b'',
            'headers': EnvironHeaders([
                ('Host', 'nolcat:5000'),
                ('Connection', 'close'),
                ('Content-Length', '261'),
                ('Cache-Control', 'max-age=0'),
                ('Origin', 'http://x.x.x.x'),
                ('Content-Type', 'application/x-www-form-urlencoded'),
                ('Upgrade-Insecure-Requests', '1'),
                ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'),
                ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'),
                ('Referer', 'http://x.x.x.x/login/'),
                ('Accept-Encoding', 'gzip, deflate'),
                ('Accept-Language', 'en-US,en;q=0.9'),
                ('Cookie', 'session=eyJjc3JmX3Rva2VuIjoiMmQ4OTkwMzQyYTkwMjVhZWI0NmQyNzQ5ZTdmZGE3MTMwNDYxZmU3NSJ9.Z9mRdA.vEqDiO4UNssMRfukIj7KdjIEW5U')
            ]),
            'remote_addr': 'x.x.x.x',
            'environ': {
                'wsgi.errors': <gunicorn.http.wsgi.WSGIErrorsWrapper object at 0x7ff055201b70>,
                'wsgi.version': (1, 0),
                'wsgi.multithread': False,
                'wsgi.multiprocess': True,
                'wsgi.run_once': False,
                'wsgi.file_wrapper': <class 'gunicorn.http.wsgi.FileWrapper'>,
                'wsgi.input_terminated': True,
                'SERVER_SOFTWARE': 'gunicorn/23.0.0',
                'wsgi.input': <gunicorn.http.body.Body object at 0x7ff055201fd0>,
                'gunicorn.socket': <socket.socket fd=9, family=2, type=1, proto=0, laddr=('x.x.x.x', 5000), raddr=('x.x.x.x', 49018)>,
                'REQUEST_METHOD': 'POST',
                'QUERY_STRING': '',
                'RAW_URI': '/login/',
                'SERVER_PROTOCOL': 'HTTP/1.0',
                'HTTP_HOST': 'nolcat:5000',
                'HTTP_CONNECTION': 'close',
                'CONTENT_LENGTH': '261',
                'HTTP_CACHE_CONTROL': 'max-age=0',
                'HTTP_ORIGIN': 'http://x.x.x.x',
                'CONTENT_TYPE': 'application/x-www-form-urlencoded',
                'HTTP_UPGRADE_INSECURE_REQUESTS': '1',
                'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'HTTP_REFERER': 'http://x.x.x.x/login/',
                'HTTP_ACCEPT_ENCODING': 'gzip, deflate',
                'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.9',
                'HTTP_COOKIE': 'session=eyJjc3JmX3Rva2VuIjoiMmQ4OTkwMzQyYTkwMjVhZWI0NmQyNzQ5ZTdmZGE3MTMwNDYxZmU3NSJ9.Z9mRdA.vEqDiO4UNssMRfukIj7KdjIEW5U',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'x.x.x.x',
                'REMOTE_PORT': '49018',
                'SERVER_NAME': '0.0.0.0',
                'SERVER_PORT': '5000',
                'PATH_INFO': '/login/',
                'SCRIPT_NAME': '',
                'werkzeug.request': <Request 'http://nolcat:5000/login/' [POST]>
            },
            'shallow': False,
            'json_module': <flask.json.provider.DefaultJSONProvider object at 0x7ff056cd79b0>,
            'cookies': ImmutableMultiDict([('session', 'eyJjc3JmX3Rva2VuIjoiMmQ4OTkwMzQyYTkwMjVhZWI0NmQyNzQ5ZTdmZGE3MTMwNDYxZmU3NSJ9.Z9mRdA.vEqDiO4UNssMRfukIj7KdjIEW5U')]),
            'url_rule': <Rule '/login/' (GET, HEAD, POST, OPTIONS) -> login.login_homepage>,
            'view_args': {},
            'stream': <gunicorn.http.body.Body object at 0x7ff055201fd0>,
            '_parsed_content_type': ('application/x-www-form-urlencoded', {}),
            'content_length': 261,
            'form': ImmutableMultiDict([
                ('csrf_token', 'IjJkODk5MDM0MmE5MDI1YWViNDZkMjc0OWU3ZmRhNzEzMDQ2MWZlNzUi.Z9mZrg.vZJr-nKGDKa8pIHC8Hta2gVps_U'),
                ('int_data', '1'),
                ('string_data', 'df'),
                ('date_data', '2025-02-25'),
                ('select_data', '2'),
                ('text_data', 'qqqqqqq'),
                ('multiple_select_data', 'a'),
                ('multiple_select_data', 'b'),
                ('multiple_file_data', 'hello_world.py')
            ]),
            'files': ImmutableMultiDict([]),
            'host': 'nolcat:5000',
            'url': 'http://nolcat:5000/login/'
        }
        '''
        '''  [2025-03-18 19:02:27] nolcat.login.views::147 - `request.headers` (type <class 'werkzeug.datastructures.headers.EnvironHeaders'>):
            Host: nolcat:5000
            Connection: close
            Content-Length: 369
            Cache-Control: max-age=0
            Origin: http://x.x.x.x
            Content-Type: application/x-www-form-urlencoded
            Upgrade-Insecure-Requests: 1
            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36
            Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
            Referer: http://x.x.x.x/login/
            Accept-Encoding: gzip, deflate
            Accept-Language: en-US,en;q=0.9
            Cookie: session=eyJjc3JmX3Rva2VuIjoiMmQ4OTkwMzQyYTkwMjVhZWI0NmQyNzQ5ZTdmZGE3MTMwNDYxZmU3NSJ9.Z9mRdA.vEqDiO4UNssMRfukIj7KdjIEW5U
        '''
        step_function_input = {
            "Bool_input": Bool_data,
            "int_input": int_data,
            "string_input": string_data,
            #"date_input": date_data,  #TEST: [2025-05-28 20:35:12] nolcat.login.views::170 - `json.dumps` on type <class 'datetime.date'> raises Object of type date is not JSON serializable
            "select_input": select_data,
            #"file_input": file_data,  #TEST: [2025-05-28 20:35:12] nolcat.login.views::180 - `json.dumps` on type <class 'werkzeug.datastructures.file_storage.FileStorage'> raises Object of type FileStorage is not JSON serializable
            "text_input": text_data,
            "multiple_select_input": multiple_select_data,
            #"multiple_file_input": multiple_file_data,  #TEST: [2025-05-28 20:35:12] nolcat.login.views::195 - `json.dumps` on type <class 'list'> raises Object of type FileStorage is not JSON serializable
        }
        #TEST: [2025-05-28 21:31:50] nolcat.login.views::172 - `json.dumps` on `workbook` of type <class 'openpyxl.workbook.workbook.Workbook'> raises Object of type Workbook is not JSON serializable
        #TEST: [2025-05-28 21:31:50] nolcat.login.views::177 - `json.dumps` on `worksheet` of type <class 'openpyxl.worksheet._read_only.ReadOnlyWorksheet'> raises Object of type ReadOnlyWorksheet is not JSON serializable

        step_functions_client.start_execution(
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/start_execution.html
            stateMachineArn=STATE_MACHINE_ARN,
            name=f"execution-{datetime.now().strftime(AWS_timestamp_format())}",  # Unique execution name
            input=json.dumps(step_function_input)  # The string that contains the JSON input data for the execution,...Length constraints apply to the payload size, and are expressed as bytes in UTF-8 encoding.
        )
        return "Workflow triggered"
    else:
        message = Flask_error_statement(form.errors)
        log.error(message)
        flash(message)
        return abort(404)


#ToDo: If individual accounts are to be used, create route to account creation page with Flask-User