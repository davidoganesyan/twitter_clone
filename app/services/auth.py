from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.user import User


async def get_current_user_from_api_key(
    api_key: str = Header(..., alias="api-key"),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> Optional[User]:
    """
    Аутентифицирует пользователя по api-key.
    """
    result = await db.execute(select(User).filter(User.api_key == api_key))
    user: Optional[User] = result.scalars().one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user
