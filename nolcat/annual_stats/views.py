import logging
from flask import render_template
from flask import request
from flask import abort
from flask import redirect
from flask import url_for
from flask import flash
import pandas as pd

from . import bp
from .forms import *
from ..app import *
from ..models import *

log = logging.getLogger(__name__)


@bp.route('/', methods=['GET', 'POST'])
def annual_stats_homepage():
    """Returns the homepage for the `annual_stats` blueprint, which serves as a homepage for administrative functions."""
    log.info("Starting `annual_stats_homepage()`.")
    form = ChooseFiscalYearForm()
    if request.method == 'GET':
        # The links to the lists of vendors, resource sources, and statistics sources are standard jinja redirects; the code for populating the lists from the underlying relations is in the route functions being redirected to
        fiscal_year_options = query_database(
            query="SELECT fiscal_year_ID, fiscal_year FROM fiscalYears;",
            engine=db.engine,
        )
        if isinstance(fiscal_year_options, str):
            return abort(404)  #HomepageSQLError
        form.fiscal_year.choices = list(fiscal_year_options.itertuples(index=False, name=None))
        return render_template('annual_stats/index.html', form=form)
    elif form.validate_on_submit():
        fiscal_year_PK = form.fiscal_year.data
        return redirect(url_for('annual_stats.show_fiscal_year_details'))  #ToDo: Use https://stackoverflow.com/a/26957478 to add variable path information
    else:
        log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)


@bp.route('/view_year', methods=['GET', 'POST'])  #ToDo: Add variable path information accepting the PK for the fiscal year
def show_fiscal_year_details():  #ToDo: Add variable path information for the PK for the fiscal year
    """Returns a page that shows the information about and the statistics collection status for the fiscal year."""
    log.info("Starting `show_fiscal_year_details()`.")
    #ToDo: `FiscalYears.collect_fiscal_year_usage_statistics()` runs from here
    #ToDo: `AnnualUsageCollectionTracking.collect_annual_usage_statistics()` runs from here
    #ToDo: if re.fullmatch(r'SUSHI harvesting for statistics source \w* raised the error \w*\.', string=method_response[0]): above failed
    run_annual_stats_methods_form = RunAnnualStatsMethodsForm()
    edit_fiscalYear_form = EditFiscalYearForm()
    edit_AUCT_form = EditAUCTForm()
    #ToDo: is the best way to run `FiscalYears.create_usage_tracking_records_for_fiscal_year()` also a form?
    if request.method == 'GET':
        #ToDo: fiscal_year_PK = the variable path int, which is also the PK in the fiscalYears relations for the fiscal year being viewed
        fiscal_year_details = query_database(
            query=f"SELECT * FROM fiscalYears WHERE fiscal_year_ID = {fiscal_year_PK};",
            engine=db.engine,
        )
        if isinstance(fiscal_year_details, str):
            flash(f"Unable to load requested page because it relied on t{fiscal_year_details[1:].replace(' raised', ', which raised')}")
            return redirect(url_for('annual_stats.annual_stats_homepage'))
        fiscal_year_details = fiscal_year_details.astype(FiscalYears.state_data_types())
        #ToDo: Pass `fiscal_year_details` single-record dataframe to page for display
        fiscal_year_reporting = query_database(
            query=f"SELECT * FROM annualUsageCollectionTracking WHERE AUCT_fiscal_year = {fiscal_year_PK};",
            engine=db.engine,
            index='AUCT_statistics_source',
        )
        if isinstance(fiscal_year_reporting, str):
            flash(f"Unable to load requested page because it relied on t{fiscal_year_reporting[1:].replace(' raised', ', which raised')}")
            return redirect(url_for('annual_stats.annual_stats_homepage'))
        fiscal_year_reporting = fiscal_year_reporting.astype(AnnualUsageCollectionTracking.state_data_types())
        #ToDo: Pass `fiscal_year_reporting` dataframe to page for display
        return render_template('annual_stats/fiscal-year-details.html', run_annual_stats_methods_form=run_annual_stats_methods_form, edit_fiscalYear_form=edit_fiscalYear_form, edit_AUCT_form=edit_AUCT_form)
    elif run_annual_stats_methods_form.validate_on_submit():
        #ToDo: if run_annual_stats_methods_form.annual_stats_method.data is the number for `calculate_ACRL_60b()`:
            #ToDo: Flash result of `fiscal_year_PK.calculate_ACRL_60b()`
            return redirect(url_for('annual_stats.show_fiscal_year_details'))
        #ToDo: if run_annual_stats_methods_form.annual_stats_method.data is the number for `calculate_ACRL_63()`:
            #ToDo: Flash result of `fiscal_year_PK.calculate_ACRL_63()`
            return redirect(url_for('annual_stats.show_fiscal_year_details'))
        #ToDo: if run_annual_stats_methods_form.annual_stats_method.data is the number for `calculate_ARL_18()`:
            #ToDo: Flash result of `fiscal_year_PK.calculate_ARL_18()`
            return redirect(url_for('annual_stats.show_fiscal_year_details'))
        #ToDo: if run_annual_stats_methods_form.annual_stats_method.data is the number for `calculate_ARL_19()`:
            #ToDo: Flash result of `fiscal_year_PK.calculate_ARL_19()`
            return redirect(url_for('annual_stats.show_fiscal_year_details'))
        #ToDo: if run_annual_stats_methods_form.annual_stats_method.data is the number for `calculate_ARL_20()`:
            #ToDo: Flash result of `fiscal_year_PK.calculate_ARL_20()`
            return redirect(url_for('annual_stats.show_fiscal_year_details'))
    elif edit_fiscalYear_form.validate_on_submit():
        #ToDo: Upload change to `fiscalYears` relation
        #ToDo: Set up message flashing that change was made
        return redirect(url_for('annual_stats.show_fiscal_year_details'))
    elif edit_AUCT_form.validate_on_submit():
        #ToDo: Upload change to `annualUsageCollectionTracking` relation
        #ToDo: Set up message flashing that change was made
        return redirect(url_for('annual_stats.show_fiscal_year_details'))
    else:
        #ToDo: Get values below for the form submitted
        #ToDo: log.error(f"`form.errors`: {form.errors}")  #404
        return abort(404)