"""Library Media Person RESTful API"""

import uuid
import hashlib
import flask_restx
from . import app
from . import db

app = app.app
api = flask_restx.Api(app,
                      version='0.1',
                      title='LPM Index API',
                      description='API for storing info about Libraries, Media, and Persons')
# TODO validate=True

libns = api.namespace('lib', description='Library operations')
filns = api.namespace('fil', description='File operations')

lib = api.model('Lib', {'slug': flask_restx.fields.String(required=True,
                                                          description='Shorthand for library'),
                        'url': flask_restx.fields.String(description='Website of library')})
per = api.model('Per', {'slug': flask_restx.fields.String(required=True,
                                                          description='Shorthand for name'),
                        'url': flask_restx.fields.String(description='Webpage for person'),
                        'lib': flask_restx.fields.Nested(lib)})
med = api.model('Med', {'slug': flask_restx.fields.String(required=True,
                                                          description='Shorthand for title'),
                        'url': flask_restx.fields.String(description='Webpage of media'),
                        'lib': flask_restx.fields.Nested(lib),
                        'pers': flask_restx.fields.List(flask_restx.fields.Nested(per))})
fil = api.model('Fil', {'digest': flask_restx.fields.String(description='Hash of URL'),
                        'url': flask_restx.fields.String(description='Link to file', required=True),
                        'meds': flask_restx.fields.List(flask_restx.fields.Nested(med))})


# flask_restx.fields.Integer(readonly=True, description='Task ID'),
# flask_restx.fields.DateTime(readonly=True, description='When task created'),
# flask_restx.fields.Boolean(description='Eisenhower urgency'),
# flask_restx.fields.Boolean(description='Close task', default=False),
#        parser = flask_restx.reqparse.RequestParser()
#        parser.add_argument('mode', choices=('triage', 'paper'), default='open')
#        parser.add_argument('until', type=flask_restx.inputs.datetime_from_iso8601)
#        args = parser.parse_args()

@libns.route('/')
class LibList(flask_restx.Resource):
    """All libs API"""

    @libns.doc('list_libs')
    @libns.marshal_list_with(lib)
    def get(self):
        """Get all libraries"""
        return db.Lib.query.all()

    @libns.doc('create_lib')
    @libns.expect(lib)
    @libns.marshal_with(lib, code=201)
    def post(self):
        """Create library"""
        # TODO restrict
        indict = dict(api.payload)
        newlib = db.Lib(**indict)
        db.db.session.add(newlib)
        db.db.session.commit()
        return newlib, 201

# NOTE no /lib/s - immuable

@libns.route('/<lib_slug>/med/')
@libns.response(404, 'Library not found')
@libns.param('lib_slug', 'Library slug')
class LibMed(flask_restx.Resource):
    """Library media"""

    @libns.doc('list_lib_meds')
    @libns.marshal_list_with(med)
    def get(self, lib_slug):
        """Get library media"""
        # TODO omit persons?
        return db.Med.query.filter(db.Med.lib_slug == lib_slug).all()

    @libns.doc('create_lib_med')
    @libns.expect(med)
    @libns.marshal_with(med, code=201)
    def post(self, lib_slug):
        """Add media to this library"""
        indict = dict(api.payload)
        newmed = db.Med(**indict)
        newmed.lib_slug = lib_slug
        newmed.uuid = str(uuid.uuid1())
        db.db.session.add(newmed)
        db.db.session.commit()
        return newmed, 201


@libns.route('/<lib_slug>/med/<med_slug>')
@libns.response(404, 'Media not found')
@libns.param('lib_slug', 'Library slug')
@libns.param('med_slug', 'Media slug')
class MedOne(flask_restx.Resource):
    """Single media"""

    # NOTE no PUT here, do link_per_med to modify

    @libns.doc('get_media')
    @libns.marshal_with(med)
    def get(self, lib_slug, med_slug):
        """Get media with persons"""
        # NOTE persons is here
        # TODO first_or_404?
        return db.Med.query.filter(db.Med.lib_slug == lib_slug, db.Med.slug == med_slug).one()


@libns.route('/<lib_slug>/per/')
@libns.response(404, 'Library not found')
@libns.param('lib_slug', 'Library slug')
class LibPer(flask_restx.Resource):
    """Library persons"""

    @libns.doc('list_lib_pers')
    @libns.marshal_list_with(per)
    def get(self, lib_slug):
        """Get library persons"""
        # NOTE media is not here
        return db.Per.query.filter(db.Per.lib_slug == lib_slug).all()

    @libns.doc('create_lib_per')
    @libns.expect(per)
    @libns.marshal_with(per, code=201)
    def post(self, lib_slug):
        """Create a person in this library"""
        indict = dict(api.payload)
        newper = db.Per(**indict)
        newper.lib_slug = lib_slug
        newper.uuid = str(uuid.uuid1())
        db.db.session.add(newper)
        db.db.session.commit()
        return newper, 201


@libns.route('/<lib_slug>/med/<med_slug>/fil')
@libns.response(404, 'Media not found')
@libns.param('lib_slug', 'Library slug')
@libns.param('med_slug', 'Media slug')
class MedFil(flask_restx.Resource):
    """Media files"""

    # NOTE no POST, do create_fil

    @libns.doc('get_media_files')
    @libns.marshal_with(med)
    def get(self, lib_slug, med_slug):
        """Get the files that contain this media"""
        # TODO first_or_404?
        return db.Med.query.filter(db.Med.lib_slug == lib_slug, db.Med.slug == med_slug).one().fils


@libns.route('/<lib_slug>/per/<per_slug>/med')
@libns.response(404, 'Person not found')
@libns.param('lib_slug', 'Library slug')
@libns.param('per_slug', 'Person slug')
class PerMed(flask_restx.Resource):
    """Personal media"""

    @libns.doc('get_person_media')
    @libns.marshal_with(med)
    def get(self, lib_slug, per_slug):
        """Get the media for this person"""
        # TODO first_or_404?
        return db.Per.query.filter(db.Per.lib_slug == lib_slug, db.Per.slug == per_slug).one().meds

    @libns.doc('link_per_med')
    @libns.expect(med)
    @libns.marshal_with(med, code=201)
    def post(self, lib_slug, per_slug):
        """Link this person to a media"""
        # TODO first_or_404?
        myper = db.Per.query.filter(db.Per.lib_slug == lib_slug, db.Per.slug == per_slug).one()
        # TODO 4xx
        mymed = db.Med.query.filter(db.Med.lib_slug == lib_slug,
                                    db.Med.slug == api.payload['slug']).one()
        # TODO deal with truly new media
        myper.meds.append(mymed)
        db.db.session.commit()
        return mymed, 201


# TODO GET /lib/s/per/s


@filns.route('/')
class FilAll(flask_restx.Resource):
    """All Files"""

    @filns.doc('create_fil')
    @filns.expect(fil)
    @filns.marshal_with(fil, code=201)
    def post(self):
        """Create file"""
        # TODO restrict
        # TODO allow non truly new file with new media association
        # TODO allow lazy or new media file associations
        indict = dict(api.payload)
        mymeds = indict.pop('meds', [])
        newfil = db.Fil(**indict)
        newfil.digest = hashlib.sha1(newfil.url.encode()).hexdigest()
        for mymed in mymeds:
            foundmed = db.Med.query.filter(db.Med.lib_slug == mymed['lib_slug'],
                                           db.Med.slug == mymed['slug']).one()
            newfil.meds.append(foundmed)
        db.db.session.add(newfil)
        db.db.session.commit()
        return newfil, 201


@filns.route('/<fil_digest>')
@filns.response(404, 'File not found')
@filns.param('fil_digest', 'File URL digest')
class FilOne(flask_restx.Resource):
    """Single file"""

    # NOTE no PUT here, redo POST /fil

    @filns.doc('get_file')
    @filns.marshal_with(fil)
    def get(self, fil_digest):
        """Get file info"""
        # NOTE media is here
        # TODO omit persons
        return db.Fil.query.get_or_404(fil_digest)

# TODO add actual links instead of objects/slugs
