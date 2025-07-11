import logging
from sqlalchemy import log as SQLAlchemy_log


def filter_empty_parentheses(log_statement):
    """A filter removing log statements containing only empty parentheses.

    SQLAlchemy logging has lines for outputting query parameters, but since pandas doesn't use parameters, these lines always appear in stdout as empty parentheses. This function and its use in `nolcat.app.create_logging()` is based upon information at https://stackoverflow.com/a/58583082.

    Args:
        log_statement (logging.LogRecord): a Python logging statement

    Returns:
        bool: if `log_statement` should go to stdout
    """
    if log_statement.name == "sqlalchemy.engine.base.Engine" and log_statement.msg == "%r":
        return False
    elif log_statement.name == "sqlalchemy.engine.base.Engine" and re.search(r"\n\s+", log_statement.msg):
        log_statement.msg = remove_IDE_spacing_from_statement(log_statement.msg)
        return True
    else:
        return True


def configure_logging(app):
    """Create single logging configuration for entire program.

    This function was largely based upon the information at https://shzhangji.com/blog/2022/08/10/configure-logging-for-flask-sqlalchemy-project/ (site no longer available) with some additional information from https://engineeringfordatascience.com/posts/python_logging/. The logging level and format set in `logging.basicConfig` are used when directly running NoLCAT in the container; the `nolcat/pytest.ini` supplies that information when using pytest. The module `sqlalchemy.engine.base.Engine` is used for the SQLAlchemy logger instead of the more common `sqlalchemy.engine` because the latter includes log statements from modules `sqlalchemy.engine.base.Engine` and `sqlalchemy.engine.base.OptionEngine`, which are repeats of one another.

    Args:
        app (flask.Flask): the Flask object

    Returns:
        None: no return value is needed, so the default `None` is used
    """
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(name)s::%(lineno)d - %(message)s",  # "[timestamp] module name::line number - error message"
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding="utf-8",
        force=True,  # With this argument and a call to the function before `logging.getLogger()`, Glue jobs can use this logging config
    )
    logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.INFO)  # Statements appear when when no live log output is requested
    logging.getLogger('sqlalchemy.engine.base.Engine').addFilter(filter_empty_parentheses)  # From Python docs: "Multiple calls to `getLogger()` with the same name will always return a reference to the same Logger object."
    SQLAlchemy_log._add_default_handler = lambda handler: None  # Patch to avoid duplicate logging (from https://stackoverflow.com/a/76498428)
    logging.getLogger('botocore').setLevel(logging.INFO)  # This prompts `s3transfer` module logging to appear
    logging.getLogger('s3transfer.utils').setLevel(logging.INFO)  # Expected log statements seem to be set at debug level, so this hides all log statements
    if app.debug:
        logging.getLogger('werkzeug').handlers = []  # Prevents Werkzeug from outputting messages twice in debug mode