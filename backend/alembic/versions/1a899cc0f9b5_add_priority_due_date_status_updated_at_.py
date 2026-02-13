"""add_priority_due_date_status_updated_at_to_tasks

Revision ID: 1a899cc0f9b5
Revises: 32f5b9a61834
Create Date: 2026-02-12 04:03:02.287743

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a899cc0f9b5'
down_revision: Union[str, Sequence[str], None] = '32f5b9a61834'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns
    op.add_column('task', sa.Column('status', sa.String(length=20), nullable=False, server_default='todo'))
    op.add_column('task', sa.Column('priority', sa.String(length=10), nullable=True, server_default='medium'))
    op.add_column('task', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))

    # Migrate existing data: convert completed boolean to status
    op.execute("""
        UPDATE task
        SET status = CASE
            WHEN completed = true THEN 'done'
            ELSE 'todo'
        END
    """)

    # Drop the old completed column
    op.drop_column('task', 'completed')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the completed column
    op.add_column('task', sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'))

    # Migrate data back: convert status to completed boolean
    op.execute("""
        UPDATE task
        SET completed = CASE
            WHEN status = 'done' THEN true
            ELSE false
        END
    """)

    # Drop the new columns
    op.drop_column('task', 'updated_at')
    op.drop_column('task', 'due_date')
    op.drop_column('task', 'priority')
    op.drop_column('task', 'status')
