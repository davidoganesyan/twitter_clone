import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.media import Media
from app.schemas.media_schemas import MediaUploadResponse

router = APIRouter(prefix="/api/medias", tags=["Media"])


@router.post("/", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
):
    """
    Загружает медиафайл и возвращает его ID.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        MEDIA_ROOT = "/media"
        os.makedirs(MEDIA_ROOT, exist_ok=True)
        file_path = os.path.join(MEDIA_ROOT, file.filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        new_media = Media(file_path=f"/media/{file.filename}")
        db.add(new_media)
        await db.commit()
        await db.refresh(new_media)

        return {"result": True, "media_id": new_media.id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
