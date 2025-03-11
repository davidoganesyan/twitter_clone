import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (  # type: ignore
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.database import Base, get_db
from app.models.follow import Follower  # noqa
from app.models.like import Like  # noqa
from app.models.media import Media
from app.models.tweet import Tweet
from app.models.user import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
# TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine):
    async with async_sessionmaker(engine)() as session:
        yield session


@pytest.fixture
async def app(engine):
    app = FastAPI()

    async def override_get_db():
        async with async_sessionmaker(engine)() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    from main import app as main_app

    app.include_router(main_app.router)

    return app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_users(session: AsyncSession):
    await session.execute(delete(User))
    await session.commit()
    user1 = User(name="Test User 1", api_key="api-key-1")
    user2 = User(name="Test User 2", api_key="api-key-2")

    session.add_all([user1, user2])
    await session.commit()


@pytest.fixture
async def test_media(session: AsyncSession):
    await session.execute(delete(Media))
    await session.commit()
    media1 = Media(file_path="test1.jpg")
    media2 = Media(file_path="test2.jpg")

    session.add_all([media1, media2])
    await session.commit()


@pytest.fixture
async def test_tweets(session: AsyncSession, test_users, test_media):
    await session.execute(delete(Tweet))
    await session.commit()
    tweet1 = Tweet(content="Test Tweet 1", author_id=1)
    tweet2 = Tweet(content="Test Tweet 2", author_id=2)

    session.add_all([tweet1, tweet2])
    await session.commit()
