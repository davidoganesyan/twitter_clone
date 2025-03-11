from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.follow import Follower
from app.models.like import Like
from app.models.media import Media
from app.models.tweet import Tweet
from app.models.user import User


async def populate_database(db: AsyncSession):
    """
    Наполняет базу данных тестовыми данными для демонстрации работы приложения.
    """
    try:
        user1 = User(api_key="user1_api_key", name="Alice")
        user2 = User(api_key="user2_api_key", name="Bob")
        user3 = User(api_key="user3_api_key", name="Charlie")
        user4 = User(api_key="test", name="JustMe")

        db.add_all([user1, user2, user3, user4])
        await db.flush()

        tweet1 = Tweet(content="Hello, world!", author_id=user1.id)
        tweet2 = Tweet(content="This is my first tweet!", author_id=user2.id)
        tweet3 = Tweet(content="Python is awesome!", author_id=user3.id)
        tweet4 = Tweet(content="And Me again!", author_id=user4.id)

        db.add_all([tweet1, tweet2, tweet3, tweet4])
        await db.flush()

        media1 = Media(file_path="/media/image1.jpeg", tweet_id=tweet1.id)
        media2 = Media(file_path="/media/image2.jpeg", tweet_id=tweet2.id)
        media3 = Media(file_path="/media/image3.jpeg", tweet_id=tweet3.id)

        db.add_all([media1, media2, media3])
        await db.flush()

        like1 = Like(user_id=user2.id, tweet_id=tweet1.id)
        like2 = Like(user_id=user3.id, tweet_id=tweet1.id)
        like3 = Like(user_id=user1.id, tweet_id=tweet2.id)
        like4 = Like(user_id=user4.id, tweet_id=tweet2.id)
        like5 = Like(user_id=user4.id, tweet_id=tweet1.id)
        like6 = Like(user_id=user4.id, tweet_id=tweet3.id)

        db.add_all([like1, like2, like3, like4, like5, like6])
        await db.flush()

        follow1 = Follower(follower_id=user2.id, followed_id=user1.id)
        follow2 = Follower(follower_id=user3.id, followed_id=user1.id)
        follow3 = Follower(follower_id=user1.id, followed_id=user2.id)
        follow4 = Follower(follower_id=user1.id, followed_id=user3.id)
        follow5 = Follower(follower_id=user1.id, followed_id=user4.id)

        db.add_all([follow1, follow2, follow3, follow4, follow5])
        await db.commit()

        print("Database populated successfully!")

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error populating database: {e}")
