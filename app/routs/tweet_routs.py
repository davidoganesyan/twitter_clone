from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.models.follow import Follower
from app.models.like import Like
from app.models.media import Media
from app.models.tweet import Tweet
from app.models.user import User
from app.schemas.tweet_schemas import (
    FeedResponse,
    LikeResponse,
    TweetCreate,
    TweetResponse,
)
from app.services.auth import get_current_user_from_api_key

router = APIRouter(prefix="/api/tweets", tags=["Tweets"])


@router.post("/", response_model=TweetResponse)
async def post_tweet(
    tweet_data: TweetCreate,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user_from_api_key),  # noqa: B008
):
    """
    Создает новый твит.
    """
    try:
        new_tweet = Tweet(content=tweet_data.tweet_data, author_id=current_user.id)
        db.add(new_tweet)
        await db.flush()
        if tweet_data.tweet_media_ids:
            for media_id in tweet_data.tweet_media_ids:
                media_result = await db.execute(
                    select(Media).filter(Media.id == media_id)
                )
                media: Optional[Media] = media_result.scalars().first()
                if media:
                    media.tweet_id = new_tweet.id
        tweet_id = new_tweet.id
        await db.commit()
        return {"result": True, "tweet_id": tweet_id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=401, detail=str(e))


@router.delete("/{tweet_id}", response_model=dict)
async def delete_tweet(
    tweet_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user_from_api_key),  # noqa: B008
):
    """
    Удаляет твит, если он принадлежит текущему пользователю.
    """
    try:
        tweet_result = await db.execute(select(Tweet).filter(Tweet.id == tweet_id))
        tweet: Optional[Tweet] = tweet_result.scalars().first()
        if not tweet or tweet.author_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You can only delete your own tweets"
            )
        await db.delete(tweet)
        await db.commit()
        return {"result": True}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/{tweet_id}/likes", response_model=LikeResponse)
async def like_tweet(
    tweet_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user_from_api_key),  # noqa: B008
):
    """
    Добавляет лайк к твиту.
    """
    try:
        tweet_result = await db.execute(select(Tweet).filter(Tweet.id == tweet_id))
        tweet: Optional[Tweet] = tweet_result.scalars().first()
        if not tweet:
            raise HTTPException(status_code=404, detail="Tweet not found")

        existing_like_result = await db.execute(
            select(Like).filter(
                Like.tweet_id == tweet_id, Like.user_id == current_user.id
            )
        )
        existing_like: Optional[Like] = existing_like_result.scalars().first()
        if existing_like:
            raise HTTPException(status_code=400, detail="You already liked this tweet")

        new_like = Like(user_id=current_user.id, tweet_id=tweet_id)
        db.add(new_like)
        await db.commit()
        return {"result": True}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tweet_id}/likes", response_model=LikeResponse)
async def unlike_tweet(
    tweet_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user_from_api_key),  # noqa: B008
):
    """
    Удаляет лайк с твита.
    """
    try:
        like_result = await db.execute(
            select(Like).filter(
                Like.tweet_id == tweet_id, Like.user_id == current_user.id
            )
        )
        like: Optional[Like] = like_result.scalars().first()
        if not like:
            raise HTTPException(status_code=404, detail="Like not found")

        await db.delete(like)
        await db.commit()
        return {"result": True}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=FeedResponse)
async def get_feed(
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user_from_api_key),  # noqa: B008
):
    """
    Возвращает ленту твитов от пользователей, на которых подписан текущий пользователь,
    отсортированную по количеству лайков (включая твиты без лайков).
    """
    try:
        following = await db.execute(
            select(Follower.followed_id).filter(Follower.follower_id == current_user.id)
        )
        following_ids = [row[0] for row in following.fetchall()]
        following_ids.append(current_user.id)

        tweets_query = (
            select(
                Tweet,
                func.count(Like.id).label("like_count"),
            )
            .outerjoin(Tweet.likes)
            .options(
                selectinload(Tweet.author),
                selectinload(Tweet.media),
                selectinload(Tweet.likes).selectinload(Like.user),
            )
            # .filter(Tweet.author_id.in_(following_ids))
            .group_by(Tweet.id)
            .order_by(func.count(Like.id).desc())
        )

        tweets_result = await db.execute(tweets_query)
        tweets_with_likes = tweets_result.all()

        feed = [
            {
                "id": tweet.id,
                "content": tweet.content,
                "attachments": [media.file_path for media in tweet.media],
                "author": {"id": tweet.author.id, "name": tweet.author.name},
                "likes": [
                    {"user_id": like.user_id, "name": like.user.name}
                    for like in tweet.likes
                ],
            }
            for tweet, _ in tweets_with_likes
        ]

        return {"result": True, "tweets": feed}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
