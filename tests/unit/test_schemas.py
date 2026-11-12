"""Request validation."""
import pytest
from pydantic import ValidationError

from app.models.user import UserRole
from app.schemas.user import UserCreate

VALID = dict(full_name="Ada Rider", email="ada@example.com", password="pw", role="rider")


def test_valid_user_is_accepted():
    user = UserCreate(**VALID)
    assert user.role is UserRole.RIDER
    assert user.phone_number is None


def test_invalid_email_is_rejected():
    with pytest.raises(ValidationError):
        UserCreate(**{**VALID, "email": "not-an-email"})


def test_unknown_role_is_rejected():
    with pytest.raises(ValidationError):
        UserCreate(**{**VALID, "role": "superuser"})
