from flask import Flask
from flask import render_template
from flask_wtf.csrf import CSRFProtect

from nolcat.ingest import forms  #ToDo: If routes are still in this file when `view` blueprint is added, add `as ingest_forms`

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
        form = AForm()
        return render_template('index.html', form=form)

    @app.route('/check', methods=["GET","POST"])
    def submit_check():
        form = AForm()
        if form.validate_on_submit():
            return render_template('ok.html', val=form.name.data)
        return render_template('index.html')

    return app
