from datetime import datetime, timezone
from typing import Optional, Dict, Any

def calculate_fetch_health(
    meta_fetch_time: Optional[datetime],
    shopify_fetch_time: Optional[datetime]
) -> Dict[str, Any]:
    """
    Calculates the fetch health status based on the age of the last successful fetches.
    Returns a dictionary with ages in hours and a composite health status.
    """
    now = datetime.now(timezone.utc)
    
    # Normalize naive datetimes to UTC
    if meta_fetch_time and meta_fetch_time.tzinfo is None:
        meta_fetch_time = meta_fetch_time.replace(tzinfo=timezone.utc)
    if shopify_fetch_time and shopify_fetch_time.tzinfo is None:
        shopify_fetch_time = shopify_fetch_time.replace(tzinfo=timezone.utc)

    age_meta_hours = (now - meta_fetch_time).total_seconds() / 3600 if meta_fetch_time else float('inf')
    age_shopify_hours = (now - shopify_fetch_time).total_seconds() / 3600 if shopify_fetch_time else float('inf')

    # Determine status based on older of the two data sources
    max_age = max(age_meta_hours, age_shopify_hours)

    if max_age >= 6 or max_age == float('inf'):
        status = "red"
    elif max_age >= 2:
        status = "amber"
    else:
        status = "green"

    return {
        "last_successful_fetch_meta_at": meta_fetch_time,
        "last_successful_fetch_shopify_at": shopify_fetch_time,
        "age_meta_hours": round(age_meta_hours, 2) if meta_fetch_time else None,
        "age_shopify_hours": round(age_shopify_hours, 2) if shopify_fetch_time else None,
        "fetch_health_status": status,
    }
