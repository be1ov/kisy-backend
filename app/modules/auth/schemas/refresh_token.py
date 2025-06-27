from datetime import datetime

from pydantic import BaseModel


class RefreshTokenSchema(BaseModel):
    user_id: str
    exp: datetime