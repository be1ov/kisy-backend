import typing as tp
from pydantic import BaseModel


class CreateGoodSchema(BaseModel):
    id: tp.Optional[str]
    title: str
    description: str
    show_in_catalog: tp.Optional[bool] = True
