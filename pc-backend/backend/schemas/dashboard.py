from marshmallow import Schema, fields

class PaginatedCampaignCommandSchema(Schema):
    rows = fields.List(fields.Dict)
    pagination = fields.Dict# ======= CCV v2 Schemas (APPEND-ONLY) =======
from marshmallow import Schema, fields, validate
from datetime import timezone, timedelta

class CampaignCommandRequestSchema(Schema):
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    bm_ids = fields.List(fields.Int(), load_default=list)
    master_store_ids = fields.List(fields.Str(), load_default=list)
    campaign_status = fields.List(fields.Str(), load_default=list)
    mode = fields.Str(validate=validate.OneOf(["native", "usd"]), load_default="native")
    page = fields.Int(validate=validate.Range(min=1), load_default=1)
    page_size = fields.Int(validate=validate.Range(min=1, max=100), load_default=20)

class CampaignSchema(Schema):
    campaign_id = fields.Str(required=True)
    campaign_name = fields.Str(allow_none=True)
    campaign_status = fields.Str(allow_none=True)
    currency_code = fields.Str(allow_none=True)
    date = fields.Date(allow_none=True)

    # monetary / metric fields (as strings to preserve precision)
    ad_budget = fields.Decimal(as_string=True, allow_none=True, places=2)
    spend_raw = fields.Decimal(as_string=True, allow_none=True, places=2)
    shopify_orders = fields.Int(allow_none=True)
    shopify_revenue = fields.Decimal(as_string=True, allow_none=True, places=2)
    clicks = fields.Int(allow_none=True)
    impressions = fields.Int(allow_none=True)
    landing_page_views = fields.Int(allow_none=True)
    results = fields.Int(allow_none=True)
    purchase_conversion_value_meta_raw = fields.Decimal(as_string=True, allow_none=True, places=2)

    # derived
    ad_budget_spend_pct = fields.Float(allow_none=True)
    true_roas = fields.Float(allow_none=True)
    aov = fields.Float(allow_none=True)
    ctr_link = fields.Float(allow_none=True)
    cost_per_lpv = fields.Float(allow_none=True)

class BMTotalsSchema(Schema):
    bm_id = fields.Int(required=True)
    bm_name = fields.Str(required=True)
    shopify_orders = fields.Int()
    shopify_revenue = fields.Decimal(as_string=True, places=2)
    spend_raw = fields.Decimal(as_string=True, places=2)
    true_roas = fields.Float()
    aov = fields.Float()

class ScopedTotalsSchema(Schema):
    shopify_orders = fields.Int()
    shopify_revenue = fields.Decimal(as_string=True, places=2)
    spend_raw = fields.Decimal(as_string=True, places=2)
    true_roas = fields.Float()
    aov = fields.Float()

class ScopedSummarySchema(Schema):
    start_date = fields.Date()
    end_date = fields.Date()
    mode = fields.Str()
    bm_ids = fields.List(fields.Int())
    master_store_ids = fields.List(fields.Str())
    bm_names = fields.List(fields.Str())
    master_store_names = fields.List(fields.Str())
    bm_totals = fields.List(fields.Nested(BMTotalsSchema))
    scoped_totals = fields.Nested(ScopedTotalsSchema)

class GroupSchema(Schema):
    bm_id = fields.Int(required=True)
    bm_name = fields.Str(required=True)
    master_store_id = fields.Str(allow_none=True)
    master_store_name = fields.Str(allow_none=True)
    style_class = fields.Str(allow_none=True)

    # fetch-health block
    last_successful_fetch_meta_at = fields.DateTime(allow_none=True)
    last_successful_fetch_shopify_at = fields.DateTime(allow_none=True)
    age_meta_hours = fields.Float(allow_none=True)
    age_shopify_hours = fields.Float(allow_none=True)
    fetch_health_status = fields.Str(allow_none=True)

    campaigns = fields.List(fields.Nested(CampaignSchema))

class PaginationSchema(Schema):
    page = fields.Int()
    page_size = fields.Int()
    total_items = fields.Int()
    total_pages = fields.Int()

class CampaignCommandResponseSchema(Schema):
    exported_at = fields.DateTime()  # stored UTC; UI will render local
    scoped_summary = fields.Nested(ScopedSummarySchema)
    pagination = fields.Nested(PaginationSchema)
    groups = fields.List(fields.Nested(GroupSchema))

    # Optional helper if you later want a localized string:
    def format_exported_local(self, obj):
        dt = obj.get("exported_at")
        if dt is None:
            return None
        # Asia/Karachi ~ UTC+05:00
        return dt.astimezone(timezone(timedelta(hours=5))).isoformat()
# ======= /CCV v2 Schemas =======
