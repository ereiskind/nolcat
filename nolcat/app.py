from flask import Flask

def create_app():
    """A factory pattern for instantiating Flask web apps."""
    app = Flask(__name__)

    @app.route('/')
    def homepage():
        return "This is the homepage"

    return app