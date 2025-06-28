from pydantic import BaseModel

class UserUpdateSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
