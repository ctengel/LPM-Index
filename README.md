# LPM-Index
Library Person Media Index

A SQL RDBMS based system to track libraries and their constituent people and media, along with appearances, and files depicting said media.

## API

Prereqs
- Python 3
- flask
- flask-restx
- flask-sqlalchemy
- some sqlalchemy DB engine; sqlite is fine for testing

To run the API, first create a config file like so:

```
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:////path/to/database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Next, create the schema:
```
$ LPMIA_SETTINGS=/path/to/config.cfg python3 -m lpm_index_api.db_create
```

From here, the API itself can be run:
```
$ FLASK_APP=lpm_index_api.api LPMIA_SETTINGS=/path/to/config.cfg flask run
 * Serving Flask app "lpm_index_api.api"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

From there you can navigate to http://127.0.0.1:5000/ for a Swagger OpenAPI spec doc showing you all that is possible
