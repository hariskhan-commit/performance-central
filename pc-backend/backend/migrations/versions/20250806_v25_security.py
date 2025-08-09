"""v25 security features

Revision ID: 20250806_v25_security
Revises: 20250805_v24_full_schema
Create Date: 2025-08-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20250806_v25_security'
down_revision = '20250805_v24_full_schema'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False, index=True),  # bcrypt hash
        sa.Column('key_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('owner_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True),
        sa.Column('bm_id', sa.Integer(), sa.ForeignKey('business_manager_configs.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True),
        sa.Column('scopes', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('rate_limit', sa.String(), default="60/minute", nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked', sa.Boolean(), default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_api_keys_active', 'api_keys', ['id'], postgresql_where=sa.text('revoked = false'))

    op.create_table('webauthn_credentials',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False),
        sa.Column('cred_id', sa.String(), unique=True, nullable=False),
        sa.Column('public_key', sa.LargeBinary(), nullable=False),
        sa.Column('sign_count', sa.Integer(), nullable=False),
        sa.Column('transports', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('webauthn_credentials')
    op.drop_index('ix_api_keys_active', table_name='api_keys')
    op.drop_table('api_keys')