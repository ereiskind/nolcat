import logging
from flask import render_template
from flask import request
from flask import abort
from flask import redirect
from flask import url_for

from . import bp
from ..app import db
from .forms import ChooseFiscalYearForm
#from ..models import <name of SQLAlchemy classes used in views below>


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")  # This formatting puts the appearance of these logging messages largely in line with those of the Flask logging messages


@bp.route('/', methods=['GET', 'POST'])
def annual_stats_homepage():
    """Returns the homepage for the `annual_stats` blueprint, which serves as a homepage for administrative functions."""
    form = ChooseFiscalYearForm()
    if request.method == 'GET':
        # The links to the lists of vendors, resource sources, and statistics sources are standard jinja redirects; the code for populating the lists from the underlying relations is in the route functions being redirected to
        fiscal_year_options = pd.read_sql(
            sql="SELECT fiscal_year_ID, fiscal_year FROM fiscalYears;",
            con=db.engine,
        )
        form.fiscal_year.choices = list(fiscal_year_options['fiscal_year_ID', 'fiscal_year'].itertuples(index=False, name=None))
        return render_template('annual_stats/index.html', form=form)
    elif form.validate_on_submit():
        fiscal_year_PK = form.fiscal_year.data
        return redirect(url_for('show_fiscal_year_details'))  #ToDo: Use https://stackoverflow.com/a/26957478 to add variable path information
    else:
        return abort(404)


#ToDo: Create route for details of a fiscal year
    # return fiscal_year_details.html


#ToDo: Create route for `annualUsageCollectionTracking` which uses a variable route to filter just a single fiscal year and displays all the records for that fiscal year