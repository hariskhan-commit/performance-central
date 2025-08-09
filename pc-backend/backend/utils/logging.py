import logging
from pythonjsonlogger import jsonlogger
from flask import g

class CorrelationIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = g.get('request_id', '-')
        return True

def init_logging(app):
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s'
    )
    handler.setFormatter(formatter)
    handler.addFilter(CorrelationIDFilter())
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    for celery_logger in ('celery.app.trace', 'celery.worker'):
        logging.getLogger(celery_logger).handlers = [handler]