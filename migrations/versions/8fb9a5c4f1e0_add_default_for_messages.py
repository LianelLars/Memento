"""Add default for messages

Revision ID: 8fb9a5c4f1e0
Revises: 0d377dfc7c6e
Create Date: 2024-04-15 19:54:36.010599

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8fb9a5c4f1e0'
down_revision: Union[str, None] = '0d377dfc7c6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
