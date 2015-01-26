from proctopy import app
from tasks import process_upload_task
import rethinkdb as r
from rethinkdb.errors import RqlDriverError

from flask import Response, request, abort, g, jsonify, json
from werkzeug import secure_filename

PROCTOPY_DB = app.config.get('RETHINK_DB') or 'proctopus'
RDB_HOST =  app.config.get('RETHINK_HOST') or 'localhost'
RDB_PORT = app.config.get('RETHINK_PORT') or 28015


@app.before_request
def before_request():
    try:
        g.rdb_conn = r.connect(host=RDB_HOST, port=RDB_PORT, db=PROCTOPY_DB)
    except RqlDriverError:
        abort(503, "No database connection could be established.")

@app.teardown_request
def teardown_request(exception):
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass

@app.route("/upload", methods=['POST'])
def process_upload():
    headers = request.headers

    if request.json:
        # request was sent with application/json mimetype
        # so parse the json
        try:
            response = _process_post_json(request.json)
        except:
            abort(400, "Exception parsing json")
    else:
        # determine if we have a multipart upload, otherwise return a 400 bad request
        files = request.files.getlist('file')
        if not files:
            abort(400, "No files uploaded")

        response = _process_multipart_data(files)

    return response



def _process_post_json(blob):
    """Processes uploads made through JSON request. The only currently supported
    uploads via JSON are through the 'file_urls' property, which is a list of URI.

    Acceptable JSON properties:

        * file_urls - list of URLs to fetch and process
        * emails - [] of emails to send processed results to, if not empty.
        * storage_destinations  - [] of storage mechanisms. Supported right now are: dropbox, local
    """
    data = blob

    errors = {}
    work_request = {}

    try:
        file_urls = data['file_urls']
        work_request['urls'] = file_urls
    except KeyError:
        errors.setdefault('missing_fields', list()).append('file_urls')

    emails = data.get('emails')
    if emails:
        work_request['emails'] = emails

    storage_destinations = data.get('storage_destinations', list())

    for sd in storage_destinations:
        if sd not in app.config['SUPPORTED_STORAGE_LOCATIONS']:
            errors.setdefault('messages', list()).append(
                '{0} is not a supported storage location'.format(sd)
            )

    if errors:
        # return a 400 and the JSON
        return Response(json.dumps(errors), status=400, mimetype='application/json')

    if storage_destinations:
        work_request['storage_destinations'] = storage_destinations

    inserted = r.table('requests').insert(
     {
        'status': 'WAITING',
     }
    ).run(g.rdb_conn)

    work_request['request_id'] = inserted['generated_keys'][0]

    process_upload_task.delay(work_request)

    # summon the message queue!
    response = {
        "request_id": work_request['request_id']
    }

    return Response(json.dumps(response), mimetype='application/json')



def _process_multipart_data(files):
    # obtain the headers from the request
    # supported headers are:
    # X-proctopy-emails - a comma-separated list of email addresses
    # X-proctopy-storage-destinations - a comma-separated list of destinations
    inserted = r.table('requests').insert(
     {
        'status': 'WAITING',
     }
    ).run(g.rdb_conn)

    work_request['request_id'] = inserted['generated_keys'][0]

    work_request = {}
    for f in files:
        filename = secure_filename(f.filename)
        outfile = "{0}/{1}-{2}".format(app.config['TMP_PATH'],
            work_request['request_id'], filename)
        f.save(outfile)
        work_request.setdefault('files', list()).append(outfile)

    process_upload_task(work_request).delay

    response = {
        "request_id": work_request['request_id']
    }

    return Response(json.dumps(response), mimetype='application/json')

@app.route("/status/<string:request_id>", methods=['GET'])
def get_status(request_id):
    request = r.table('requests').get(request_id).run(g.rdb_conn)
    return json.dumps(request)
