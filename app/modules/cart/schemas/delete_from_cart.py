import typing

from pydantic import BaseModel


class DeleteFromCartSchema(BaseModel):
    variation_id: str
    quantity: typing.Optional[int]