from datetime import datetime, timedelta
from backend.tasks import app
from backend.utils.db import get_db_session
from backend.models.core import BusinessManagerConfig, MetaTokenStatus
from flask import current_app
import requests

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def update_token_statuses(self):
    soon = datetime.utcnow() + timedelta(days=3)
    with get_db_session() as session:
        try:
            expiring = session.query(BusinessManagerConfig).filter(
                BusinessManagerConfig.meta_token_expires_at <= soon,
                BusinessManagerConfig.meta_token_status == MetaTokenStatus.ACTIVE
            ).all()
            for bm in expiring:
                bm.meta_token_status = MetaTokenStatus.EXPIRING
            session.commit()
        except Exception as e:
            session.rollback()
            raise self.retry(exc=e)

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def refresh_tokens(self):
    with get_db_session() as session:
        try:
            expiring = session.query(BusinessManagerConfig).filter(
                BusinessManagerConfig.meta_token_status.in_([MetaTokenStatus.EXPIRING, MetaTokenStatus.EXPIRED])
            ).all()
            for bm in expiring:
                try:
                    response = requests.post("https://api.example.com/refresh", data={"token": bm.meta_user_access_token_reference})
                    if response.ok:
                        new_token = response.json()["new_token"]
                        bm.meta_user_access_token_reference = new_token
                        bm.meta_token_expires_at = datetime.utcnow() + timedelta(days=60)
                        bm.meta_token_status = MetaTokenStatus.ACTIVE
                        bm.meta_token_last_refreshed_at = datetime.utcnow()
                    else:
                        raise Exception("Refresh failed")
                except Exception as e:
                    current_app.logger.error(f"Token refresh failed for BM {bm.id}: {e}")
                    requests.post("https://slack.webhook.url", json={"text": f"Token refresh failed for BM {bm.id}"})
            session.commit()
        except Exception as e:
            session.rollback()
            raise self.retry(exc=e)