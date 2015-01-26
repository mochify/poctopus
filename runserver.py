#!/usr/bin/env python

from proctopy import app

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError


if __name__ == '__main__':
    # initialize the database
    host = app.config.get('RETHINK_HOST') or 'localhost'
    port = app.config.get('RETHINK_PORT') or 28015
    db   = app.config.get('RETHINK_DB') or 'proctopus'

    connection = r.connect(host=host, port=port)
    try:
        r.db_create(db).run(connection)
        print 'proctopy database initialized'
    except RqlRuntimeError:
        print 'Database already initialized'

    try:
        r.db(db).table_create('requests').run(connection)
        print 'requests table initialized'
    except RqlRuntimeError:
        print 'requests table already initialized'
    finally:
        connection.close()


    app.run()
