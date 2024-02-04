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


class CreateUserSchema(ModelSchema):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
        )


class PatchUserSchema(ModelSchema):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "gender",
        )
        fields_optional = "__all__"
