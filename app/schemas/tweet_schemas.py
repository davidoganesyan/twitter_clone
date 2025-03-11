from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"tweet_data": "Hello, world!", "tweet_media_ids": [1, 2]}
        }
    )


class TweetResponse(BaseModel):
    result: bool
    tweet_id: int

    model_config = ConfigDict(
        json_schema_extra={"example": {"result": True, "tweet_id": 1}}
    )


class TweetInFeed(BaseModel):
    id: int
    content: str
    attachments: Optional[List[str]] = None
    author: dict
    likes: List[dict]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "content": "Hello, world!",
                "attachments": ["images/image1.jpg"],
                "author": {"id": 1, "name": "Alice"},
                "likes": [{"user_id": 2, "name": "Bob"}],
            }
        }
    )


class FeedResponse(BaseModel):
    result: bool
    tweets: List[TweetInFeed]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "result": True,
                "tweets": [
                    {
                        "id": 1,
                        "content": "Hello, world!",
                        "attachments": ["images/image1.jpg"],
                        "author": {"id": 1, "name": "Alice"},
                        "likes": [{"user_id": 2, "name": "Bob"}],
                    }
                ],
            }
        }
    )


class LikeResponse(BaseModel):
    result: bool

    model_config = ConfigDict(json_schema_extra={"example": {"result": True}})
