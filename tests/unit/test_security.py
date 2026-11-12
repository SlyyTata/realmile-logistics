"""Password hashing and JWT creation."""
from datetime import datetime, timezone

import pytest
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password


def test_hash_is_not_the_plain_password():
    hashed = hash_password("s3cret-pass")
    assert hashed != "s3cret-pass"
    assert hashed.startswith("$argon2")


def test_same_password_hashes_differently_each_time():
    # Argon2 adds a random salt, so two hashes of one password never match
    assert hash_password("s3cret-pass") != hash_password("s3cret-pass")


def test_verify_password_accepts_correct_and_rejects_wrong():
    hashed = hash_password("s3cret-pass")
    assert verify_password("s3cret-pass", hashed) is True
    assert verify_password("wrong-pass", hashed) is False


def test_access_token_contains_subject_and_expiry():
    token = create_access_token("rider@example.com")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload["sub"] == "rider@example.com"
    minutes_left = (
        datetime.fromtimestamp(payload["exp"], tz=timezone.utc) - datetime.now(timezone.utc)
    ).total_seconds() / 60
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES - 1 < minutes_left <= settings.ACCESS_TOKEN_EXPIRE_MINUTES


def test_token_signed_with_another_key_is_rejected():
    token = create_access_token("rider@example.com")
    with pytest.raises(JWTError):
        jwt.decode(token, "a-different-key", algorithms=[settings.ALGORITHM])


def test_tampered_token_is_rejected():
    header, payload, signature = create_access_token("rider@example.com").split(".")
    forged = jwt.encode({"sub": "admin@example.com"}, "attacker-key", algorithm="HS256").split(".")[1]
    with pytest.raises(JWTError):
        jwt.decode(f"{header}.{forged}.{signature}", settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
