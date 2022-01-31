from pathlib import Path
from flask import Flask
from flask import render_template
from flask_wtf.csrf import CSRFProtect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from nolcat.ingest import forms  #ToDo: If routes are still in this file when `view` blueprint is added, add `as ingest_forms`

csrf = CSRFProtect()

def page_not_found(error):
    """Returns the 404 page when a HTTP 404 error is raised."""
    return render_template('404.html'), 404


def create_app():
    """A factory pattern for instantiating Flask web apps."""
    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)
    csrf.init_app(app)
    #ToDo: Replace regerating secret key with reference to container environment variable
    app.config['SECRET_KEY'] = "ReplaceMeLater"
    app.config['UPLOAD_FOLDER'] = './data'

    from nolcat import ingest
    app.register_blueprint(ingest.bp)

    from nolcat import view
    app.register_blueprint(view.bp)

    @app.route('/')
    def homepage():
        """Returns the homepage in response to web app root requests."""
        #ToDo: Add login for `ingest` blueprint
        #ToDo: Add login for `view` blueprint
        return render_template('index.html')
    

    #Section: Routes Involving Forms
    #ToDo: Figure out how to manage CSRF tokens with a nested source code folder
    @app.route('/enter-data')
    def enter_data():
        form = forms.TestForm()
        return render_template('enter-data.html', form=form)

    @app.route('/check', methods=["GET","POST"])
    def submit_check():
        form = forms.TestForm()
        if form.validate_on_submit():
            return render_template('ok.html', val=form.string.data)
        return render_template('index.html')

    return app


def Chrome_browser_driver():
    """Creates a Selenium webdriver for a headless Chrome browser."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--verbose')
    chrome_options.add_experimental_option("prefs", {
            "download.default_directory": "Downloads",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
    })
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')

    ''' From the first program
    Path_to_ChromeDriver = Path('..', 'usr', 'local', 'bin', 'chromedriver.exe') # On Windows, "chromedriver" must include the ".exe" extension; on Linux, when the file extension is included, there's a WebDriverException with the message "'chromedriver.exe' executable needs to be in PATH."
    return webdriver.Chrome(options=chrome_options, executable_path=Path_to_ChromeDriver)
    '''
    return webdriver.Chrome(options=chrome_options)