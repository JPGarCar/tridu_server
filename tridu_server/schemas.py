from typing import List

from ninja import Schema


class BulkCreateResponseSchema(Schema):
    created: int
    duplicates: int
    errors: List[str]
    message: str
    items: List[str]
