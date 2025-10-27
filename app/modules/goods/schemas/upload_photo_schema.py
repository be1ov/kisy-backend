from pydantic import BaseModel


class UploadPhotoSchema(BaseModel):
    url: str
