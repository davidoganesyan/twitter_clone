import os
from typing import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass


DATABASE_URL = (
    f'postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:'
    f'{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("DB_HOST")}'
    f':5432/{os.environ.get("POSTGRES_DB")}'
)

engine = create_async_engine(DATABASE_URL)
# engine = create_async_engine("sqlite+aiosqlite:///./app.db")


AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
