from contextlib import contextmanager
from flask import g, current_app

@contextmanager
def get_db_session():
    if not hasattr(g, 'db_session'):
        g.db_session = current_app.async_session()
    try:
        yield g.db_session
    finally:
        g.db_session.close()
        del g.db_session