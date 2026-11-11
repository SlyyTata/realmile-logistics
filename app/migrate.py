"""
Applies all pending alembic migrations, then exits.

Used by the `migrate` service in docker-compose and the `migrate` container in
the ECS task definition:  python -m app.migrate
There is no alembic.ini in the repo, so alembic is configured here in code.
"""
from alembic import command
from alembic.config import Config


def main() -> None:
    cfg = Config()
    cfg.set_main_option("script_location", "alembic")
    command.upgrade(cfg, "head")
    print("Migrations applied. Database is at:")
    command.current(cfg)


if __name__ == "__main__":
    main()
