from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask import render_template

csrf = CSRFProtect()

def create_app():
    """A factory pattern for instantiating Flask web apps."""
    app = Flask(__name__)
    csrf.init_app(app)
    #ToDo: Replace regerating secret key with reference to container environment variable
    app.config['SECRET_KEY'] = "ReplaceMeLater"

    from nolcat import ingest
    app.register_blueprint(ingest.bp)

    @app.route('/')
    def homepage():
        return render_template('index.html')

    return app