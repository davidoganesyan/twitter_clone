from typing import List

from pydantic import BaseModel, ConfigDict


class UserProfile(BaseModel):
    id: int
    name: str
    followers: List[dict]
    following: List[dict]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Alice",
                "followers": [{"id": 2, "name": "Bob"}],
                "following": [{"id": 3, "name": "Charlie"}],
            }
        }
    )


class UserResponse(BaseModel):
    result: bool
    user: UserProfile

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "result": True,
                "user": {
                    "id": 1,
                    "name": "Alice",
                    "followers": [{"id": 2, "name": "Bob"}],
                    "following": [{"id": 3, "name": "Charlie"}],
                },
            }
        }
    )


class FollowResponse(BaseModel):
    result: bool

    model_config = ConfigDict(json_schema_extra={"example": {"result": True}})
