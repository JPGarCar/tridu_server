from ninja import ModelSchema

from checkins.models import CheckIn


class CheckInSchema(ModelSchema):
    depends_on: "CheckInSchema" = None

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
