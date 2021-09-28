from flask import Flask

def create_app():
    """A factory pattern for instantiating Flask web apps."""
    app = Flask(__name__)

    return app