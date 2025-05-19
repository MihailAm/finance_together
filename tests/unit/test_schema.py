import pytest
from pydantic import ValidationError

from app.users.schema import UserSchema


def test_user_schema_valid():
    user = UserSchema(
        id=1,
        name="John",
        surname="Doe",
        email="john@example.com"
    )
    assert user.email == "john@example.com"


def test_user_schema_invalid_email():
    with pytest.raises(ValidationError):
        UserSchema(
            id=1,
            name="John",
            surname="Doe",
            email="invalid-email"
        )


def test_user_schema_invalid_id_type():
    with pytest.raises(ValidationError):
        UserSchema(id="one", name="Ivan", surname="Ivanov", email="ivan@example.com")


def test_user_schema_missing_field():
    with pytest.raises(ValidationError):
        UserSchema(id=1, name="Ivan", email="ivan@example.com")
