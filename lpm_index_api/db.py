"""Library Media Person Database"""

import flask_sqlalchemy
from . import app

db = flask_sqlalchemy.SQLAlchemy(app)
app = app.app

# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-one
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
# TODO timestamps

# db.Column(db.Integer)
# db.Column(db.Boolean, default=False)
# db.Column(db.Text)
# db.Column(db.DateTime, default=datetime.datetime.now)
# db.Column(db.DateTime, onupdate=datetime.datetime.now)

# TODO type
fil_med = db.Table('fil_med',
                   db.Column('fil_digest',
                             db.String(64),
                             db.ForeignKey('fil.digest'),
                             primary_key=True),
                   db.Column('med_uuid',
                             db.String(32),
                             db.ForeignKey('med.uuid'),
                             primary_key=True))

per_med = db.Table('per_med',
                   db.Column('per_uuid',
                             db.String(32),
                             db.ForeignKey('per.uuid'),
                             primary_key=True),
                   db.Column('med_uuid',
                             db.String(32),
                             db.ForeignKey('med.uuid'),
                             primary_key=True))


class Lib(db.Model):
    """Library table"""
    # TODO name, description, metadata
    slug = db.Column(db.String(4), primary_key=True)
    url = db.Column(db.String(64))
    pers = db.relationship('Per', backref='lib', lazy=True)
    meds = db.relationship('Med', backref='lib', lazy=True)


class Per(db.Model):
    """Person table"""
    # TODO name, description, metadata
    slug = db.Column(db.String(16))  # TODO uniq
    lib_slug = db.Column(db.String(4), db.ForeignKey('lib.slug'), nullable=False)
    url = db.Column(db.String(128))
    uuid = db.Column(db.String(32), primary_key=True)  # TODO better type
    meds = db.relationship('Med',
                           secondary=per_med,
                           lazy='subquery',
                           backref=db.backref('pers', lazy=True))


class Med(db.Model):
    """Media table"""
    # TODO name, description, metadata
    slug = db.Column(db.String(16))  # TODO uniq
    lib_slug = db.Column(db.String(4), db.ForeignKey('lib.slug'), nullable=False)
    url = db.Column(db.String(128))
    uuid = db.Column(db.String(32), primary_key=True)  # TODO better type
    fils = db.relationship('Fil',
                           secondary=fil_med,
                           lazy='subquery',
                           backref=db.backref('meds', lazy=True))


class Fil(db.Model):
    """File table"""
    # TODO metadata, source
    url = db.Column(db.String(256))
    digest = db.Column(db.String(64), primary_key=True)  # TODO better type


# TODO tag_med


#if __name__ == '__main__':
#    db.create_all()
