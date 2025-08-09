from backend.tasks import app
from requests import get
from backend.models.aggregated import FXDailyRate
from backend.config import Config
from backend.utils.db import get_db_session
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import select

@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def fetch_fx_rates(self):
    with get_db_session() as session:
        try:
            response = get(f"{Config.FX_API_URL}/latest")
            if response.status_code == 200:
                rates = response.json()['rates']
                for from_curr, rate in rates.items():
                    new_rate = FXDailyRate(date=date.today(), from_currency=from_curr, to_currency='USD', rate=Decimal(rate), source='exchangerate.host')
                    session.add(new_rate)
                session.commit()
            else:
                raise Exception("FX API failed")
        except Exception as e:
            current_app.logger.warning(f"FX fetch failed: {e} - falling back to last known rates")
            last_day = date.today() - timedelta(days=1)
            last_rates = session.query(FXDailyRate).filter_by(date=last_day).all()
            for r in last_rates:
                fallback = FXDailyRate(date=date.today(), from_currency=r.from_currency, to_currency=r.to_currency, rate=r.rate, source='fallback')
                session.add(fallback)
            session.commit()