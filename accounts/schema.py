from ninja import ModelSchema

from accounts.models import User


class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "is_active",
            "gender",
            "is_staff",
            "is_superuser",
        )
