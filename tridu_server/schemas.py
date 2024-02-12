from typing import List

from ninja import Schema


class BulkCreateResponseSchema(Schema):
    """
    Schema for bulk create response, allows server to respond with items created,
    and errors limiting specific instances from being created.
    """

    created: int
    duplicates: int
    errors: List[str]
    message: str
    items: List[str]


class ErrorObjectSchema(Schema):
    """
    Schema for the error object as described in decisions_api.md
    """

    title: str
    status: int
    details: str
