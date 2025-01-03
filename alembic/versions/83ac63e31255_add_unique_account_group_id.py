"""add_unique_account_group_id

Revision ID: 83ac63e31255
Revises: 2013dbf4da49
Create Date: 2025-01-03 16:08:00.079111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83ac63e31255'
down_revision: Union[str, None] = '2013dbf4da49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'accounts', ['group_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'accounts', type_='unique')
    # ### end Alembic commands ###