from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any

# NOTE:
# This is a SAFE SKELETON that does not import the full app stack.
# We'll fill real DB queries and grouping later.

async def get_campaign_command_v2_data(session, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal, valid response shape so the API layer can integrate immediately.
    Will be expanded to:
      - query campaign_command_snapshot
      - compute BM-level totals & scoped totals
      - integrate fetch-health
      - support USD mode via fx utils
    """
    start_date = params.get("start_date")
    end_date = params.get("end_date")
    page = int(params.get("page", 1))
    page_size = int(params.get("page_size", 20))
    mode = params.get("mode", "native")

    # Empty dataset placeholder
    data = _build_empty_response(
        start_date=start_date,
        end_date=end_date,
        mode=mode,
        page=page,
        page_size=page_size,
    )
    return data


def _build_empty_response(
    *,
    start_date,
    end_date,
    mode: str,
    page: int,
    page_size: int,
) -> Dict[str, Any]:
    return {
        "exported_at": datetime.now(timezone.utc),
        "scoped_summary": {
            "start_date": start_date,
            "end_date": end_date,
            "mode": mode,
            "bm_ids": [],
            "master_store_ids": [],
            "bm_names": [],
            "master_store_names": [],
            "bm_totals": [],
            "scoped_totals": {
                "shopify_orders": 0,
                "shopify_revenue": 0,
                "spend_raw": 0,
                "true_roas": 0.0,
                "aov": 0.0,
            },
        },
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": 0,
            "total_pages": 0,
        },
        "groups": [],
    }
