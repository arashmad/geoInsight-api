"""align aoi area type with model

Revision ID: 040fc9d484b2
Revises: ed3c8b876611
Create Date: 2026-05-12 06:11:19.824026

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '040fc9d484b2'
down_revision: Union[str, Sequence[str], None] = 'ed3c8b876611'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
