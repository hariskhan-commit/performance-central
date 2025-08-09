from marshmallow import Schema, fields

class PaginatedCampaignCommandSchema(Schema):
    rows = fields.List(fields.Dict)
    pagination = fields.Dict