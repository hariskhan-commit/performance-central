"""v24 full schema

Revision ID: 20250805_v24_full_schema
Revises: 
Create Date: 2025-08-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20250805_v24_full_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    # Enums
    op.execute("CREATE TYPE storetype AS ENUM ('MASTER', 'CHILD', 'UNKNOWN')")
    op.execute("CREATE TYPE metatokenstatus AS ENUM ('ACTIVE', 'EXPIRED', 'EXPIRING', 'INVALID')")
    op.execute("CREATE TYPE fetchstatus AS ENUM ('PENDING', 'OK', 'ERROR')")

    # Tables
    op.create_table('regions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('product_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('slug', sa.String(length=80), nullable=False),
        sa.Column('description', sa.String(length=512), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('full_name', sa.String(length=120), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('totp_secret', sa.LargeBinary(), nullable=True),  # Encrypted
        sa.Column('mfa_enabled', sa.Boolean(), default=False, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table('master_store_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('shopify_domain', sa.String(length=255), nullable=False),
        sa.Column('store_type', sa.Enum('storetype'), nullable=False),
        sa.Column('shopify_store_id', sa.String(length=32), nullable=True),
        sa.Column('api_access_token', sa.String(length=255), nullable=True),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('shopify_domain')
    )
    op.create_index(op.f('ix_master_store_configs_id'), 'master_store_configs', ['id'], unique=False)
    op.create_index(op.f('ix_master_store_configs_region_id'), 'master_store_configs', ['region_id'], unique=False)

    op.create_table('business_manager_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('master_store_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('child_shopify_domain', sa.String(length=255), nullable=False),
        sa.Column('meta_bm_id', sa.String(length=50), nullable=False),
        sa.Column('meta_app_id_used', sa.String(length=50), nullable=True),
        sa.Column('meta_user_access_token_reference', sa.String(length=255), nullable=True),
        sa.Column('meta_token_expires_at', sa.DateTime(timezone=False), nullable=True),
        sa.Column('meta_token_status', sa.Enum('metatokenstatus'), nullable=False),
        sa.Column('meta_user_agent_list', sa.Text(), nullable=True),
        sa.Column('random_delay_min_seconds', sa.Float(), nullable=True),
        sa.Column('random_delay_max_seconds', sa.Float(), nullable=True),
        sa.Column('suggested_cron_schedule_notes', sa.Text(), nullable=True),
        sa.Column('meta_fetcher_function_name_do', sa.String(length=100), nullable=True),
        sa.Column('shopify_fetcher_function_name_do', sa.String(length=100), nullable=True),
        sa.Column('meta_token_last_refreshed_at', sa.DateTime(timezone=False), nullable=True),
        sa.Column('shopify_token_last_refreshed_at', sa.DateTime(timezone=False), nullable=True),
        sa.Column('bm_identifier_custom', sa.String(length=255), nullable=True),
        sa.Column('has_active_meta_campaigns', sa.Boolean(), nullable=False),
        sa.Column('current_product_category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('last_successful_fetch_meta_at', sa.DateTime(timezone=False), nullable=True),
        sa.Column('last_successful_fetch_shopify_at', sa.DateTime(timezone=False), nullable=True),
        sa.Column('last_fetch_status_meta', sa.Enum('fetchstatus'), nullable=True),
        sa.Column('last_fetch_status_shopify', sa.Enum('fetchstatus'), nullable=True),
        sa.Column('last_error_message_meta', sa.Text(), nullable=True),
        sa.Column('last_error_message_shopify', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['current_product_category_id'], ['product_categories.id'], ondelete='RESTRICT', onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['master_store_id'], ['master_store_configs.id'], ondelete='RESTRICT', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('child_shopify_domain'),
        sa.UniqueConstraint('master_store_id', 'name'),
        sa.UniqueConstraint('meta_bm_id')
    )
    op.create_index(op.f('ix_business_manager_configs_current_product_category_id'), 'business_manager_configs', ['current_product_category_id'], unique=False)
    op.create_index(op.f('ix_business_manager_configs_master_store_id'), 'business_manager_configs', ['master_store_id'], unique=False)
    op.create_index(op.f('ix_business_manager_configs_meta_token_status'), 'business_manager_configs', ['meta_token_status'], unique=False)
    op.create_index('ix_business_manager_configs_active', 'business_manager_configs', ['id'], postgresql_where=sa.text('deleted_at IS NULL AND is_active = true'))

    op.create_table('bm_profit_assumptions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bm_id', sa.Integer(), nullable=False),
        sa.Column('profit_margin_pct', sa.Float(), nullable=False),
        sa.Column('fixed_costs', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('variable_costs_pct', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['bm_id'], ['business_manager_configs.id'], ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('meta_daily_performance',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.String(length=50), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('spend_raw', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('clicks', sa.Integer(), nullable=False),
        sa.Column('impressions', sa.Integer(), nullable=False),
        sa.Column('results', sa.Integer(), nullable=False),
        sa.Column('purchase_conversion_value_meta_raw', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_meta_daily_performance_campaign_date', 'meta_daily_performance', ['campaign_id', 'date'], unique=True)

    op.create_table('shopify_daily_sales_summary',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('master_store_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('summary_date', sa.Date(), nullable=False),
        sa.Column('orders_count', sa.Integer(), nullable=False),
        sa.Column('gross_sales_raw', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['master_store_id'], ['master_store_configs.id'], ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_shopify_daily_summary_store_date', 'shopify_daily_sales_summary', ['master_store_id', 'summary_date'], unique=True)

    op.create_table('shopify_child_daily_sales_summary',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bm_id', sa.Integer(), nullable=False),
        sa.Column('summary_date', sa.Date(), nullable=False),
        sa.Column('orders_count', sa.Integer(), nullable=False),
        sa.Column('gross_sales_raw', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['bm_id'], ['business_manager_configs.id'], ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_shopify_child_daily_summary_bm_date', 'shopify_child_daily_sales_summary', ['bm_id', 'summary_date'], unique=True)

    op.create_table('master_store_daily_summary',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('master_store_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_revenue', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('total_ad_spend', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['master_store_id'], ['master_store_configs.id'], ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_master_store_daily_summary_store_date', 'master_store_daily_summary', ['master_store_id', 'date'], unique=True)

    op.create_table('kpi_daily_snapshot',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bm_id', sa.Integer(), nullable=True),
        sa.Column('product_category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('revenue', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('ad_spend', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('roas', sa.Float(), nullable=False),
        sa.Column('cpa', sa.Float(), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['bm_id'], ['business_manager_configs.id'], ondelete='CASCADE', onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['product_category_id'], ['product_categories.id'], ondelete='CASCADE', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_kpi_daily_snapshot_bm_date', 'kpi_daily_snapshot', ['bm_id', 'date'], unique=False)

    op.create_table('fx_daily_rates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('from_currency', sa.String(length=3), nullable=False),
        sa.Column('to_currency', sa.String(length=3), nullable=False),
        sa.Column('rate', sa.DECIMAL(precision=10, scale=6), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date', 'from_currency', 'to_currency', 'source')
    )
    op.create_index('ix_fx_daily_rates_date_from', 'fx_daily_rates', ['date', 'from_currency'], unique=False)

    op.create_table('meta_campaign_data',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('campaign_id', sa.String(length=50), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('ad_budget', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('reach', sa.Integer(), nullable=False),
        sa.Column('landing_page_views', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_meta_campaign_data_campaign_date', 'meta_campaign_data', ['campaign_id', 'date'], unique=True)

def downgrade():
    op.drop_index('ix_meta_campaign_data_campaign_date', table_name='meta_campaign_data')
    op.drop_table('meta_campaign_data')
    op.drop_index('ix_fx_daily_rates_date_from', table_name='fx_daily_rates')
    op.drop_table('fx_daily_rates')
    op.drop_index('ix_kpi_daily_snapshot_bm_date', table_name='kpi_daily_snapshot')
    op.drop_table('kpi_daily_snapshot')
    op.drop_index('ix_master_store_daily_summary_store_date', table_name='master_store_daily_summary')
    op.drop_table('master_store_daily_summary')
    op.drop_index('ix_shopify_child_daily_summary_bm_date', table_name='shopify_child_daily_sales_summary')
    op.drop_table('shopify_child_daily_sales_summary')
    op.drop_index('ix_shopify_daily_summary_store_date', table_name='shopify_daily_sales_summary')
    op.drop_table('shopify_daily_sales_summary')
    op.drop_index('ix_meta_daily_performance_campaign_date', table_name='meta_daily_performance')
    op.drop_table('meta_daily_performance')
    op.drop_table('bm_profit_assumptions')
    op.drop_index('ix_business_manager_configs_active', table_name='business_manager_configs')
    op.drop_index(op.f('ix_business_manager_configs_meta_token_status'), table_name='business_manager_configs')
    op.drop_index(op.f('ix_business_manager_configs_master_store_id'), table_name='business_manager_configs')
    op.drop_index(op.f('ix_business_manager_configs_current_product_category_id'), table_name='business_manager_configs')
    op.drop_table('business_manager_configs')
    op.drop_index(op.f('ix_master_store_configs_region_id'), table_name='master_store_configs')
    op.drop_index(op.f('ix_master_store_configs_id'), table_name='master_store_configs')
    op.drop_table('master_store_configs')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('product_categories')
    op.drop_table('regions')
    op.execute('DROP TYPE storetype')
    op.execute('DROP TYPE metatokenstatus')
    op.execute('DROP TYPE fetchstatus')
    op.execute('DROP EXTENSION "uuid-ossp"')