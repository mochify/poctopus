from flask import Flask

app = Flask(__name__)

app.config.from_envvar('PROCTOPY_SETTINGS')

if 'DEFAULT_STORAGE_LOCATION' not in app.config:
    app.config.update(DEFAULT_STORAGE_LOCATION='local')

if 'SUPPORTED_STORAGE_LOCATIONS' not in app.config:
    app.config.update(SUPPORTED_STORAGE_LOCATIONS=['local'])

if 'MAILGUN_API_KEY' not in app.config:
    app.config.update(
        EMAIL_SUPPORT=False
    )
else:
    app.config.update(
        EMAIL_SUPPORT=True
    )


import proctopy.api
