from celery import Celery
from celery.utils.log import get_task_logger
from proctopy import app as flask_app
from image import process_image, process_external_file
from email import send_email

import rethinkdb as r

logger = get_task_logger(__name__)

celery = Celery('proctopy.tasks')
celery.conf.update(flask_app.config)


def save_local(files):
    save_dir = flask_app.config.get('STORAGE_PATH')
    for f in files:
        for t in ['thumbnail', 'original']:
            filename = "{0}/{1}-{2}.jpg".format(save_dir, f['name'], t)
            with open(filename, 'w') as ofile:
                ofile.write(f[t].getvalue())


fn_map = {
    'local': save_local
}

@celery.task
def process_upload_task(work_request):
    # use the work_request and
    # if the request has 'urls', then offload to
    # image.process_external_files

    # if the request has 'files', then offload to
    # image.process_files
    logger.info("Processing work request {0}".format(work_request))
    dbhost = flask_app.config.get('RETHINK_HOST') or 'localhost'
    dbport = flask_app.config.get('RETHINK_PORT') or 28015
    dbname = flask_app.config.get('RETHINK_DB') or 'proctopus'

    connection = r.connect(host=dbhost, port=dbport)

    r.db(dbname).table('requests').get(work_request['request_id']).replace(
        {
            'id': work_request['request_id'],
            'status': 'PROCESSING'
        }
    )

    results = list()

    try:
        urls = work_request['urls']
        for u in urls:
            results.append(process_external_file(u))
    except KeyError:
        # we have normal files to process
        files = work_request['files']
        for f in files:
            results.append(result = process_image(f))

    # now store the file (or whatever)
    destinations = work_request.get('storage_destinations') or [flask_app.config.get('DEFAULT_STORAGE_LOCATION')]

    for d in destinations:
        fn_map[d](results)

    emails = work_request.get("emails")
    if emails and flask_app.config.get('EMAIL_SUPPORT'):
        logger.info("Sending email for {0}".format(work_request['request_id']))
        # send email attachments
        response = send_email(emails, work_request['request_id'], results)
        logger.info(response.status_code)
        logger.info(response.text)
        logger.info(response.url)

    replace = r.db(dbname).table('requests').get(work_request['request_id']).replace(
        {
            'id': work_request['request_id'],
            'status': 'COMPLETE',
            'file_ids': [str(x.get('name')) for x in results]
        }
    ).run(connection)

    cleanup_files(results)

    logger.info(replace)
    connection.close()


def cleanup_files(results):
    for f in results:
        for key in f:
            try:
                f[key].close()
            except:
                pass
