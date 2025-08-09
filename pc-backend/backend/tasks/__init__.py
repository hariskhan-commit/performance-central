from celery import Celery
from backend.config import Config
from celery.schedules import crontab

app = Celery('backend', broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)
app.conf.task_default_queue = 'default'
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True
app.conf.broker_transport_options = {'visibility_timeout': 3600}
app.conf.result_expires = 3600
app.conf.task_default_retry_delay = 300
app.conf.task_max_retries = 3
app.conf.task_retry_backoff = True
app.conf.task_retry_backoff_max = 700
app.conf.task_routes = {
    'backend.tasks.cleanup.cleanup_old_data': {'queue': 'maintenance'},
    'backend.tasks.token_updater.refresh_tokens': {'queue': 'maintenance'},
}
app.conf.beat_schedule = {
    'cleanup-old-data': {
        'task': 'backend.tasks.cleanup.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),
    },
    'update-token-statuses': {
        'task': 'backend.tasks.token_updater.update_token_statuses',
        'schedule': crontab(minute=0, hour='*/3'),
    },
    'refresh-tokens': {
        'task': 'backend.tasks.token_updater.refresh_tokens',
        'schedule': crontab(minute=0, hour=4),
    },
    'fetch-fx-rates': {
        'task': 'backend.tasks.fx.fetch_fx_rates',
        'schedule': crontab(minute=0, hour=5),
    },
    'purge-expired-keys': {
        'task': 'backend.tasks.security.purge_expired_keys',
        'schedule': crontab(minute=0, hour='*/1'),
    },
}

app.conf.task_queues = (
    Queue('default'),
    Queue('maintenance'),
    Queue('dead_letter', exchange='dead_letter', routing_key='dead_letter'),
)
app.conf.task_default_exchange = 'tasks'
app.conf.task_default_exchange_type = 'direct'
app.conf.task_default_routing_key = 'default'