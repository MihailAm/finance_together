"""update_planned_expenses

Revision ID: 146ad5ad9b51
Revises: 7470ba24f110
Create Date: 2025-02-25 16:57:13.742862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '146ad5ad9b51'
down_revision: Union[str, None] = '7470ba24f110'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('planned_expenses', sa.Column('name', sa.String(), nullable=False))
    op.add_column('planned_expenses', sa.Column('is_active_pay', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('planned_expenses', 'is_active_pay')
    op.drop_column('planned_expenses', 'name')
    # ### end Alembic commands ###
