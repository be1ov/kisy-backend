from pydantic import BaseModel


class CountryEntity(BaseModel):
    name: str
    code: str