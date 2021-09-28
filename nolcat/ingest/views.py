from . import bp


@bp.route('/initialize-database')
def start_R4_data_load():
    """Returns the page where the CSVs with R4 data are selected."""
    return "a file selection field that supports selecting multiple files that goes to determine_if_resources_match when submitted"


@bp.route('/matching')
def determine_if_resources_match():
    """Transforms all the formatted R4 reports into a single RawCOUNTERReport object, deduplicates the resources, and returns a page asking for confirmation of manual matches."""
    return "a form containing the metadata for each potential resource match pair with a checkbox for indicating if it is a pair and radio buttons to indicate which set of metadata to save to the Resources relation"


@bp.route('/database-creation-complete')
def data_load_complete():
    """Returns a page showing data just added to the database upon its successful loading into the database."""
    return "a page displaying the records added to the Resources, Provided_Resources, and COUNTER_Usage_Data relations"