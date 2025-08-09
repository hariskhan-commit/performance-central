from datetime import datetime
from backend.tasks import app
from backend.utils.db import get_db_session
from backend.models.security import ApiKey
from sqlalchemy import or_

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def purge_expired_keys(self):
    now = datetime.utcnow()
    with get_db_session() as session:
        try:
            expired = session.query(ApiKey).filter(
                or_(ApiKey.revoked == True, ApiKey.expires_at < now)
            ).all()
            for key in expired:
                session.delete(key)
            session.commit()
        except Exception as e:
            session.rollback()
            raise self.retry(exc=e)