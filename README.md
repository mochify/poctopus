# `poctopus`
The proctopus proof-of-concept

# Setup

## Prerequisites

### Mandatory Requirements

`poctopus` is compatible with python 2.6, python 2.7, and pypy.

* Python 2.6+ or pypy 2.4+
* pip
* virtualenv
* RethinkDB
* RabbitMQ

### Optional Requirements

`poctopus` supports some additional features if you enable them

* [dropbox](https://dropbox.com) integration - `poctopus` can store files in a user's dropbox account
* [mailgun](https://mailgun.com) integration - `poctopus` can send processed files via email using the Mailgun API

## Build and Run

* `virtualenv poctopus_env`
   * if you're using pypy, run `virtualenv -p <path/to/pypy> poctopus_env`
* `source poctopus_env/bin/activate`
* `pip install -r requirements.pip`
* `python runserver.py`

## All-in-One Bootstrap and Run

* `sh bootstrap.sh` - This will install `poctopus`'s requirements including RabbitMQ and RethinkDB.
* `source poctopus_env/bin/activate`
* Run the supervisor daemon: `poctopus_env/bin/supervisord`

This will start up all the services configured inside the `supervisord.conf` file: `poctopy` server, `celery` workers, `rabbitmq-server`, and `rethinkdb`
