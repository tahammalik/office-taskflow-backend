from typing import AsyncGenerator
import pytest_asyncio  # Add this
import pytest
from app.core.db import Base,get_db
from app.core.config import DatabaseConfig
from sqlalchemy import URL, NullPool
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from app.main import app
from httpx import ASGITransport,AsyncClient

#pytest_plugins = ["anyio"]
 
db_config = DatabaseConfig()

test_db_url = URL.create(
    drivername=db_config.drivername,
    username=db_config.username,
    password=db_config.password,
    host=db_config.host,
    port=db_config.port,
    database=db_config.database
)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(test_db_url, echo=True,poolclass=NullPool)
    return engine

@pytest.fixture(scope="session")
async def setup_db(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()

@pytest.fixture(scope="function")
async def db_session(
    test_engine,
    setup_db
)-> AsyncGenerator[AsyncSession, None]:
    conn = await test_engine.connect()
    tarns = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await tarns.rollback()
            await conn.close()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        
        base_url="http://testserver",
        transport=ASGITransport(app=app),
    ) as client:
        yield client
    
    app.dependency_overrides.clear()

