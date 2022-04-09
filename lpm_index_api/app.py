"""Library Media Person RESTful API"""

import flask


# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config.from_envvar('LPMIA_SETTINGS', silent=True)


#if __name__ == '__main__':
#    app.run()
