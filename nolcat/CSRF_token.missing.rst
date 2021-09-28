CSRF Token Missing
##################

The following conditions lead to ``"POST /matching HTTP/1.1" 400``

* "app.py" contains ``app.config['SESSION_COOKIE_SECURE'] = False`` and "select-matches.html" contains ``{{ form.csrf_token }}`` and ``{{ form.hidden_tag() }}``
* "app.py" contains ``app.config['SESSION_COOKIE_SECURE'] = False`` and "select-matches.html" contains ``{{ form.csrf_token }}``
* "app.py" contains ``app.config['SESSION_COOKIE_SECURE'] = False`` and "select-matches.html" contains ``{{ form.hidden_tag() }}``
* "select-matches.html" contains ``{{ form.csrf_token }}`` and ``{{ form.hidden_tag() }}``
* "select-matches.html" contains ``{{ form.csrf_token }}``
* "select-matches.html" contains ``{{ form.hidden_tag() }}``


Resources
*********

* https://stackoverflow.com/questions/54027777/flask-wtf-csrf-session-token-missing-secret-key-not-found
* https://stackoverflow.com/questions/21501058/form-validation-fails-due-missing-csrf (https://stackoverflow.com/questions/50695051/csrf-token-the-csrf-token-is-missing-flask-wtf is duplicate)
* https://stackoverflow.com/questions/59756059/csrf-token-is-missing-in-flask-but-it-is-rendering-in-the-template
* https://stackoverflow.com/questions/46497714/flask-wtf-csrf-token-is-missing
* https://stackoverflow.com/questions/39260241/flask-wtf-csrf-token-missing
* https://stackoverflow.com/questions/61158237/flask-wtforms-validate-on-submit-not-working
* https://stackoverflow.com/questions/52483449/session-cookie-secure-does-not-encrypt-session (on SESSION_COOKIE_SECURE, which some other responses mention)