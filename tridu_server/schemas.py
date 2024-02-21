from typing import List

from django.core.exceptions import ValidationError
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

    @staticmethod
    def from_validation_error(
        validation_error: ValidationError, instance_name: str
    ) -> "ErrorObjectSchema":
        """
        Create an error object from a validation error, status code is always 409 and message is the error message
        :param validation_error: The validation error to create this error msg from
        :param instance_name: The type name of the instance that raised the validation error
        :return: A new error object schema instance
        """
        return ErrorObjectSchema.for_validation_error(
            instance_name=instance_name,
            details=", ".join(validation_error.messages),
        )

    @staticmethod
    def for_validation_error(details: str, instance_name: str) -> "ErrorObjectSchema":
        """
        Create an error object for a validation error with a custom message, status code is always 409.
        :param details: Details of the error
        :param instance_name: The type name of the instance that has a validaitoin error
        :return:
        """
        return ErrorObjectSchema(
            title="Validation error for a {}".format(instance_name),
            status=409,
            details=details,
        )

    @staticmethod
    def from_404_error(details: str) -> "ErrorObjectSchema":
        """
        Create an error object from a 404 error, status code is always 404.
        :param details: The detailed message of the error
        :return: A new error object schema instance
        """
        return ErrorObjectSchema(
            title="Instance not found error", status=404, details=details
        )
