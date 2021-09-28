from flask import Flask
from flask import render_template

def create_app():
    """A factory pattern for instantiating Flask web apps."""
    app = Flask(__name__)

    @app.route('/')
    def homepage():
        return render_template('index.html')

    return app