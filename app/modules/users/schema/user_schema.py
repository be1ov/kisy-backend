import typing as tp
from datetime import datetime
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: tp.Optional[str] = Field(None)
    phone: tp.Optional[str] = Field(None)
    birth_date: tp.Optional[datetime] = Field(None)
    telegram_id: int
    signup_completed: bool
    is_admin: bool = False
