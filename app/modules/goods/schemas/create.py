from pydantic import BaseModel


class CreateGoodSchema(BaseModel):
    title: str
    description: str
