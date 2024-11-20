Source Code Style Guide
#######################

What follows are details about the style of the code and its documentation that have been recorded for the sake of consistent application across the code base.

reStructured Text
*****************

* Code snippets are marked with double backticks
* Per the Python style guide,

  * h1 uses hashes: ``#``
  * h2 uses asterisks: ``*``
  * h3 uses equals: ``=``
  * h4 uses dashes: ``-``
  * h5 uses carats: ``^``
  * h6 uses double quotes: ``"``

Naming Conventions
******************

* Database naming conventions are used in the codebase and the documentation

  * The Flask-SQLAlchemy relation classes are named in PascalCase, also called UpperCamelCase
  * The database itself, through the ``__tablename__`` attribute, use camelCase
  * Field names are lowercase_with_underscores

Naming Flask Routes and Webpages
================================

* Flask routes that handle data ingestion from a form will contain at least two ``return`` statements with the ``render_template`` function: one for the page the form is on, and one for each form representing the page the web app will go to when the form is submitted
* Each blueprint will have a homepage with the route ``/`` and the function name ``homepage``; Flask works best when all HTML pages have unique names