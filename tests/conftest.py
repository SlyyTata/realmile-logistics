"""Shared test setup.

The app reads its settings when it is imported, so safe defaults are set here
before any test imports it. `setdefault` means real values (e.g. the CI test
database) still win. Setting DATABASE_URL here also stops pydantic from falling
back to a local .env file, so unit tests can never touch the real Neon database.
"""
import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("DATABASE_SSL", "false")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
