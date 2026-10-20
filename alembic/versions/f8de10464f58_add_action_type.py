
"""add action type

Revision ID: f8de10464f58
Revises: b4d1848ce873
Create Date: 2026-10-20 14:57:50.902733
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "f8de10464f58"
down_revision: Union[str, Sequence[str], None] = "b4d1848ce873"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


action_type = postgresql.ENUM(
    "SET_VALUE",
    "REJECT",
    "MODIFY_VALUE",
    name="actiontype",
    create_type=False,
)


def upgrade() -> None:
    action_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "actions",
        sa.Column(
            "type",
            action_type,
            nullable=False,
            server_default="SET_VALUE",
        ),
    )

    op.alter_column("actions", "type", server_default=None)


def downgrade() -> None:
    op.drop_column("actions", "type")
    action_type.drop(op.get_bind(), checkfirst=True)
