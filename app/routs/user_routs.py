from typing import Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.follow import Follower
from app.models.user import User
from app.schemas.user_schemas import FollowResponse, UserResponse
from app.services.auth import get_current_user_from_api_key

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/{user_id}/follow", response_model=FollowResponse)
async def follow_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user_from_api_key),  # noqa: B008
):
    """
    Подписывается на пользователя.
    """
    try:
        user_to_follow: Optional[User] = (
            (await db.execute(select(User).filter(User.id == user_id)))
            .scalars()
            .first()
        )
        if not user_to_follow:
            raise HTTPException(status_code=404, detail="User not found")

        existing_follow = (
            (
                await db.execute(
                    select(Follower).filter(
                        Follower.follower_id == current_user.id,
                        Follower.followed_id == user_id,
                    )
                )
            )
            .scalars()
            .first()
        )
        if existing_follow:
            raise HTTPException(
                status_code=400, detail="You are already following this user"
            )

        new_follow = Follower(follower_id=current_user.id, followed_id=user_id)
        db.add(new_follow)
        await db.commit()
        return {"result": True}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}/follow", response_model=FollowResponse)
async def unfollow_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user_from_api_key),  # noqa: B008
):
    """
    Отписывается от пользователя.
    """
    try:
        await db.execute(
            delete(Follower).where(
                Follower.follower_id == current_user.id, Follower.followed_id == user_id
            )
        )
        await db.commit()
        return Response(
            content='{"result": true}',
            media_type="application/json",
            headers={"Cache-Control": "no-store"},
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user_from_api_key),  # noqa: B008
):
    """
    Возвращает информацию о текущем пользователе.
    """
    try:
        followers: Sequence[User] = (
            (
                await db.execute(
                    select(User)
                    .join(Follower, Follower.followed_id == User.id)
                    .filter(Follower.follower_id == current_user.id)
                )
            )
            .scalars()
            .all()
        )

        following: Sequence[User] = (
            (
                await db.execute(
                    select(User)
                    .join(Follower, Follower.follower_id == User.id)
                    .filter(Follower.followed_id == current_user.id)
                )
            )
            .scalars()
            .all()
        )

        user_profile = {
            "id": current_user.id,
            "name": current_user.name,
            "following": [
                {"id": follower.id, "name": follower.name} for follower in followers
            ],
            "followers": [
                {"id": follow.id, "name": follow.name} for follow in following
            ],
        }
        return {"result": True, "user": user_profile}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """
    Возвращает информацию о произвольном пользователе по его ID.
    """
    try:
        user: Optional[User] = (
            (await db.execute(select(User).filter(User.id == user_id)))
            .scalars()
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        followers: Sequence[User] = (
            (
                await db.execute(
                    select(User)
                    .join(Follower, Follower.followed_id == User.id)
                    .filter(Follower.follower_id == user_id)
                )
            )
            .scalars()
            .all()
        )

        following: Sequence[User] = (
            (
                await db.execute(
                    select(User)
                    .join(Follower, Follower.follower_id == User.id)
                    .filter(Follower.followed_id == user_id)
                )
            )
            .scalars()
            .all()
        )

        user_profile = {
            "id": user.id,
            "name": user.name,
            "following": [
                {"id": follower.id, "name": follower.name} for follower in followers
            ],
            "followers": [
                {"id": follow.id, "name": follow.name} for follow in following
            ],
        }
        return {"result": True, "user": user_profile}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
