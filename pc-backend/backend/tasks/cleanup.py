from datetime import date
from dateutil.relativedelta import relativedelta
from backend.tasks import app
from backend.utils.db import get_db_session
from backend.models.transactional import MetaDailyPerformance, ShopifyChildDailySalesSummary
from backend.models.aggregated import FXDailyRate
from backend.config import Config

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, rate_limit='1/m')
def cleanup_old_data(self):
    cutoff = date.today() - relativedelta(months=Config.RETENTION_MONTHS)
    with get_db_session() as session:
        try:
            for tbl in (MetaDailyPerformance, ShopifyChildDailySalesSummary, FXDailyRate):
                session.query(tbl).filter(tbl.date < cutoff).delete(synchronize_session=False)
            session.commit()
        except Exception as e:
            session.rollback()
            raise self.retry(exc=e)