import requests

from proctopy import app

mailgun_url = app.config.get('MAILGUN_URL')
mailgun_api_key = app.config.get('MAILGUN_API_KEY')
mailgun_domain = app.config.get('MAILGUN_DOMAIN')
from_address = app.config.get('MAILGUN_FROM_ADDRESS')


def send_email(emails, request_id, attachments):
    '''Attachments should be sent as file objects for now'''
    post_url = "{0}/{1}/messages".format(mailgun_url, mailgun_domain)
    files = {}

    counter = 0
    for f in attachments:
        for t in ['thumbnail', 'original']:
            filename = "{0}-{1}.jpg".format(f['name'], t)
            files['attachment[{0}]'.format(counter)] = (filename, f[t].getvalue())
            counter += 1

    return requests.post(
        post_url,
        auth=("api", mailgun_api_key),
        files = files,
        data={"from": from_address,
              "to": emails,
              "subject": "Images processed for request: {0}".format(request_id),
              "text": "Attached are processed files"})
