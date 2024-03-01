from typing import Optional

from ninja import ModelSchema

from checkins.models import CheckIn, CheckInUserBase


class CheckInSchema(ModelSchema):
    depends_on: Optional["CheckInSchema"] = None

    class Meta:
        model = CheckIn
        fields = ("id", "name", "positive_action", "negative_action")


CheckInSchema.update_forward_refs()


class CreateCheckInSchema(ModelSchema):
    depends_on: CheckInSchema | None = None

    class Meta:
        model = CheckIn
        fields = ("name", "positive_action", "negative_action")


class PatchCheckInSchema(ModelSchema):

    depends_on: CheckInSchema | None = None

    class Meta:
        model = CheckIn
        fields = ("name", "positive_action", "negative_action")
        fields_optional = "__all__"


class CheckInUserBaseSchema(ModelSchema):
    check_in: CheckInSchema

    class Meta:
        model = CheckInUserBase
        fields = (
            "is_checked_in",
            "date_changed",
        )
