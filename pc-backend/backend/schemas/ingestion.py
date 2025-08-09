from marshmallow import Schema, fields, validate

class IngestionPayload(Schema):
    bm_id = fields.Int(required=True)
    date = fields.Date(required=True)
    data_type = fields.Str(required=True, validate=validate.OneOf(["meta", "shopify_child"]))
    payload = fields.Raw(required=True)