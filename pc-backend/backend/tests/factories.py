import factory
from factory.alchemy import SQLAlchemyModelFactory
from backend.models.core import Region, ProductCategory, User, MasterStoreConfig, BusinessManagerConfig, StoreType, MetaTokenStatus
from backend.models.aggregated import FXDailyRate
from backend.models.transactional import MetaDailyPerformance, ShopifyChildDailySalesSummary, MetaCampaignData
from backend.models import async_session
from flask_bcrypt import generate_password_hash

class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = async_session
        sqlalchemy_session_persistence = "commit"

class RegionFactory(BaseFactory):
    class Meta:
        model = Region

    name = factory.Faker('word')
    currency_code = 'USD'
    is_default = True
    is_active = True

class ProductCategoryFactory(BaseFactory):
    class Meta:
        model = ProductCategory

    id = factory.Faker('uuid4')
    name = factory.Faker('word')
    slug = factory.Faker('slug')
    is_default = True
    is_active = True

class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    password_hash = factory.LazyAttribute(lambda _: generate_password_hash("password"))
    is_admin = True
    is_active = True

class MasterStoreConfigFactory(BaseFactory):
    class Meta:
        model = MasterStoreConfig

    id = factory.Faker('uuid4')
    name = factory.Faker('word')
    shopify_domain = factory.Faker('domain_name')
    store_type = StoreType.MASTER
    region = factory.SubFactory(RegionFactory)
    is_active = True

class BusinessManagerConfigFactory(BaseFactory):
    class Meta:
        model = BusinessManagerConfig

    master_store = factory.SubFactory(MasterStoreConfigFactory)
    name = factory.Faker('word')
    child_shopify_domain = factory.Faker('domain_name')
    meta_bm_id = factory.Faker('uuid4')
    current_product_category = factory.SubFactory(ProductCategoryFactory)
    is_active = True
    meta_token_status = MetaTokenStatus.ACTIVE

class FXDailyRateFactory(BaseFactory):
    class Meta:
        model = FXDailyRate

    date = factory.Faker('date_this_year')
    from_currency = 'EUR'
    to_currency = 'USD'
    rate = Decimal('1.1')
    source = 'manual'

class MetaDailyPerformanceFactory(BaseFactory):
    class Meta:
        model = MetaDailyPerformance

    campaign_id = factory.Faker('uuid4')
    date = factory.Faker('date_this_year')
    spend_raw = Decimal('100.00')
    clicks = 50
    impressions = 1000
    results = 10
    purchase_conversion_value_meta_raw = Decimal('500.00')
    currency_code = 'USD'

class ShopifyChildDailySalesSummaryFactory(BaseFactory):
    class Meta:
        model = ShopifyChildDailySalesSummary

    bm = factory.SubFactory(BusinessManagerConfigFactory)
    summary_date = factory.Faker('date_this_year')
    orders_count = 10
    gross_sales_raw = Decimal('1000.00')
    currency_code = 'USD'

class MetaCampaignDataFactory(BaseFactory):
    class Meta:
        model = MetaCampaignData

    campaign_id = factory.Faker('uuid4')
    date = factory.Faker('date_this_year')
    name = factory.Faker('word')
    status = 'active'
    ad_budget = Decimal('200.00')
    reach = 100
    landing_page_views = 50