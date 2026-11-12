"""add RETURNED to parcelstatus enum

The Parcel model has ParcelStatus.RETURNED, but the first migration left it out
of the database enum. Marking a parcel "returned" failed with a 500, and
/dashboard/stats failed on every call because its query mentions RETURNED.

Revision ID: 7c1d2e9a5b31
Revises: 4eacf3eed46b
Create Date: 2026-11-12 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '7c1d2e9a5b31'
down_revision: Union[str, Sequence[str], None] = '4eacf3eed46b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # IF NOT EXISTS makes this safe to run on a database that was patched by hand
    op.execute("ALTER TYPE parcelstatus ADD VALUE IF NOT EXISTS 'RETURNED'")


def downgrade() -> None:
    # Postgres cannot remove a value from an enum type; leaving it is harmless
    pass
