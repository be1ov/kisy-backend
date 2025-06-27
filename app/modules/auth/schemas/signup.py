from datetime import date

from pydantic import BaseModel


class SignupSchema(BaseModel):
    phone: str
    email: str
    first_name: str
    last_name: str
    birth_date: date
