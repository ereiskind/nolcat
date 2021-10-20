from pathlib import Path
from flask import Flask
from flask import render_template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def page_not_found(error):
    """Returns the 404 page when a HTTP 404 error is raised."""
    return render_template('404.html'), 404


def create_app():
    """A factory pattern for instantiating Flask web apps."""
    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)

    from nolcat import ingest
    app.register_blueprint(ingest.bp)

    #ToDo: from nolcat import view
    #ToDo: app.register_blueprint(view.bp)
    #ToDo: Create `view` blueprint

    @app.route('/')
    def homepage():
        """Returns the homepage in response to web app root requests."""
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

    return webdriver.Chrome(options=chrome_options)