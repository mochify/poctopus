import json

from proctopy import app

from flask import Response, request
from werkzeug import secure_filename

@app.route("/upload", methods=['POST'])
def process_upload():
    headers = request.headers
    print headers
    print headers['Content-Type']
    print request.files.getlist('file')
    for x in request.files.getlist('file'):
        print type(x)
        print secure_filename(x.filename)
        print x.read()

        
    #body = request.get_json()
    return Response("ok", mimetype="text/plain")

def process_post_json(blob):
    data = json.loads(blob)

def process_multipart_data(blob, files):
    pass

@app.route("/status/<string:request_id>", methods=['GET'])
def get_status():
    pass
