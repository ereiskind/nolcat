import logging
from flask import render_template
from flask import request
from flask import abort
from flask import redirect
from flask import url_for
import pandas as pd

from . import bp
from .forms import ChooseFiscalYearForm, RunAnnualStatsMethodsForm, EditFiscalYearForm, EditAUCTForm
from ..app import db
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
        form.fiscal_year.choices = list(fiscal_year_options.itertuples(index=False, name=None))
        return render_template('annual_stats/index.html', form=form)
    elif form.validate_on_submit():
        fiscal_year_PK = form.fiscal_year.data
        return redirect(url_for('annual_stats.show_fiscal_year_details'))  #ToDo: Use https://stackoverflow.com/a/26957478 to add variable path information
    else:
        logging.error(f"`form.errors`: {form.errors}")
        return abort(404)


@bp.route('/view_year', methods=['GET', 'POST'])  #ToDo: Add variable path information accepting the PK for the fiscal year
def show_fiscal_year_details():  #ToDo: Add variable path information for the PK for the fiscal year
    """Returns a page that shows the information about and the statistics collection status for the fiscal year."""
    run_annual_stats_methods_form = RunAnnualStatsMethodsForm()
    edit_fiscalYear_form = EditFiscalYearForm()
    edit_AUCT_form = EditAUCTForm()
    #ToDo: is the best way to run `FiscalYears.create_usage_tracking_records_for_fiscal_year()` also a form?
    if request.method == 'GET':
        #ToDo: fiscal_year_PK = the variable path int, which is also the PK in the fiscalYears relations for the fiscal year being viewed
        fiscal_year_details = pd.read_sql(
            sql=f"SELECT * FROM fiscalYears WHERE fiscal_year_ID = {fiscal_year_PK};",
            con=db.engine,
        )
        fiscal_year_details = fiscal_year_details.astype({
            "fiscal_year": 'string',
            "ACRL_60b": 'Int64',  # Using the pandas data type here because it allows null values
            "ACRL_63": 'Int64',  # Using the pandas data type here because it allows null values
            "ARL_18": 'Int64',  # Using the pandas data type here because it allows null values
            "ARL_19": 'Int64',  # Using the pandas data type here because it allows null values
            "ARL_20": 'Int64',  # Using the pandas data type here because it allows null values
            "notes_on_statisticsSources_used": 'string',  # For `text` data type
            "notes_on_corrections_after_submission": 'string',  # For `text` data type
        })
        #ToDo: Pass `fiscal_year_details` single-record dataframe to page for display
        fiscal_year_reporting = pd.read_sql(
            sql=f"SELECT * FROM annualUsageCollectionTracking WHERE AUCT_fiscal_year = {fiscal_year_PK};",
            con=db.engine,
            index_col='AUCT_statistics_source',
        )
        fiscal_year_reporting = fiscal_year_reporting.astype({
            "usage_is_being_collected": 'boolean',
            "manual_collection_required": 'boolean',
            "collection_via_email": 'boolean',
            "is_COUNTER_compliant": 'boolean',
            "collection_status": 'string',  # For `enum` data type
            "usage_file_path": 'string',
            "notes": 'string',  # For `text` data type
        })
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
        #ToDo: logging.error(f"`form.errors`: {form.errors}")
        return abort(404)