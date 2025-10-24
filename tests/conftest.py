import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base
from app.config import settings


pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a new engine for each test with NullPool to avoid connection reuse issues."""
    test_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    
    yield test_engine
    
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new session for each test."""
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()
