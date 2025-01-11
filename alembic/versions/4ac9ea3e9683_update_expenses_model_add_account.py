"""update_expenses_model_add_account

Revision ID: 4ac9ea3e9683
Revises: 06bdc12bcd87
Create Date: 2025-01-10 13:48:46.018064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ac9ea3e9683'
down_revision: Union[str, None] = '06bdc12bcd87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('planned_expenses', sa.Column('account_id', sa.Integer(), nullable=False))
    op.drop_constraint('planned_expenses_group_id_fkey', 'planned_expenses', type_='foreignkey')
    op.create_foreign_key(None, 'planned_expenses', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.drop_column('planned_expenses', 'group_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('planned_expenses', sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'planned_expenses', type_='foreignkey')
    op.create_foreign_key('planned_expenses_group_id_fkey', 'planned_expenses', 'groups', ['group_id'], ['id'], ondelete='CASCADE')
    op.drop_column('planned_expenses', 'account_id')
    # ### end Alembic commands ###
