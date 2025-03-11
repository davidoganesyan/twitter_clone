from pydantic import BaseModel, ConfigDict


class MediaUploadResponse(BaseModel):
    result: bool
    media_id: int

    model_config = ConfigDict(
        json_schema_extra={"example": {"result": True, "media_id": 1}}
    )
