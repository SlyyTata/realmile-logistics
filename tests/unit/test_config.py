"""Settings parsing."""
from app.core.config import Settings

REQUIRED = dict(
    DATABASE_URL="postgresql+asyncpg://u:p@localhost/db",
    SECRET_KEY="k",
    ALGORITHM="HS256",
    ACCESS_TOKEN_EXPIRE_MINUTES=60,
)


def test_cors_origins_are_split_and_trimmed():
    s = Settings(**REQUIRED, CORS_ORIGINS=" https://a.com , https://b.com ,, ")
    assert s.cors_origins_list == ["https://a.com", "https://b.com"]


def test_database_ssl_parses_false_from_text():
    assert Settings(**REQUIRED, DATABASE_SSL="false").DATABASE_SSL is False


def test_database_ssl_defaults_to_true(monkeypatch):
    # Production (Neon) needs SSL, so forgetting the setting must not disable it
    monkeypatch.delenv("DATABASE_SSL", raising=False)
    assert Settings(**REQUIRED, _env_file=None).DATABASE_SSL is True
