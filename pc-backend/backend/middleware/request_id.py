import uuid
from flask import g

def init_app(app):
    @app.before_request
    def add_request_id():
        g.request_id = str(uuid.uuid4())