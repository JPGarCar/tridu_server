from ninja import ModelSchema

from locations.models import Location


class LocationSchema(ModelSchema):
    class Meta:
        model = Location
        fields = ("id", "city", "province", "country")
