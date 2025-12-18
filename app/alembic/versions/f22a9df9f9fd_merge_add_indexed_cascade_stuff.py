"""empty message

Revision ID: f22a9df9f9fd
Revises: 52c3a21e8954, 9102b6b4e0b3
Create Date: 2025-12-18 13:14:14.364618

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f22a9df9f9fd"
down_revision: Union[str, Sequence[str], None] = ("52c3a21e8954", "9102b6b4e0b3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
