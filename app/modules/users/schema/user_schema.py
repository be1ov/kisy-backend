from datetime import datetime
from pydantic import BaseModel


class UserSchema(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    birth_date: datetime | None = None
    telegram_id: int
    signup_completed: bool
    is_admin: bool = False
