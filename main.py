from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import AsyncSessionLocal, Base, engine
from app.database.utils import populate_database
from app.routs import media_routs, tweet_routs, user_routs

# from sqlalchemy.sql import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        # await conn.execute(text("DROP SCHEMA public CASCADE"))
        # await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            await populate_database(session)
        except SQLAlchemyError as e:
            print(f"Error during database population: {e}")

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(media_routs.router)
app.include_router(tweet_routs.router)
app.include_router(user_routs.router)
