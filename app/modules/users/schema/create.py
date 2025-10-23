from pydantic import BaseModel


class UserUpdateSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    is_admin: bool | None = None
