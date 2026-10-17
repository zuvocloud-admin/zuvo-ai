import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import create_application
from app.models.tenant import Tenant
from app.models.user import User
from app.models.whatsapp_number import WhatsAppNumber
from app.models.customer import Customer


# In-memory test SQLite database
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestAsyncSessionFactory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionFactory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    app = create_application()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def seeded_tenant(db_session: AsyncSession):
    # Create Tenant
    tenant = Tenant(
        business_name="Jaipur Hardware Test Distributor",
        city="Jaipur"
    )
    db_session.add(tenant)
    await db_session.flush()

    # Create 2 Workers
    worker_1 = User(
        tenant_id=tenant.id,
        full_name="Ramesh Sharma",
        phone_number="+919829011111",
        role="WORKER",
        designation="Counter Sales"
    )
    worker_2 = User(
        tenant_id=tenant.id,
        full_name="Suresh Verma",
        phone_number="+919829022222",
        role="WORKER",
        designation="Field Sales"
    )
    db_session.add_all([worker_1, worker_2])
    await db_session.flush()

    # Map WhatsApp Lines
    num_1 = WhatsAppNumber(
        tenant_id=tenant.id,
        assigned_user_id=worker_1.id,
        meta_phone_number_id="TEST_PNID_001",
        display_phone_number="+919829011111",
        status="ACTIVE"
    )
    num_2 = WhatsAppNumber(
        tenant_id=tenant.id,
        assigned_user_id=worker_2.id,
        meta_phone_number_id="TEST_PNID_002",
        display_phone_number="+919829022222",
        status="ACTIVE"
    )
    db_session.add_all([num_1, num_2])

    # Customer
    customer = Customer(
        tenant_id=tenant.id,
        company_name="Sharma Traders Test",
        primary_phone="+919414099999"
    )
    db_session.add(customer)
    await db_session.commit()

    return {
        "tenant": tenant,
        "worker_1": worker_1,
        "worker_2": worker_2,
        "num_1": num_1,
        "num_2": num_2,
        "customer": customer
    }
