from datetime import datetime

from pydantic import BaseModel


class AccessTokenSchema(BaseModel):
    user_id: str
    exp: datetime
