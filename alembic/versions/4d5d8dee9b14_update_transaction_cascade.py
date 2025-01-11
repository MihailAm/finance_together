"""update_transaction_cascade

Revision ID: 4d5d8dee9b14
Revises: aa362257841c
Create Date: 2025-01-09 17:36:48.232101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d5d8dee9b14'
down_revision: Union[str, None] = 'aa362257841c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('finance_transactions_account_id_fkey', 'finance_transactions', type_='foreignkey')
    op.drop_constraint('finance_transactions_user_id_fkey', 'finance_transactions', type_='foreignkey')
    op.create_foreign_key(None, 'finance_transactions', 'user_profile', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'finance_transactions', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'finance_transactions', type_='foreignkey')
    op.drop_constraint(None, 'finance_transactions', type_='foreignkey')
    op.create_foreign_key('finance_transactions_user_id_fkey', 'finance_transactions', 'user_profile', ['user_id'], ['id'])
    op.create_foreign_key('finance_transactions_account_id_fkey', 'finance_transactions', 'accounts', ['account_id'], ['id'])
    # ### end Alembic commands ###