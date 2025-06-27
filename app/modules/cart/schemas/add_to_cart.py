import typing

from pydantic import BaseModel


class AddToCartSchema(BaseModel):
    variation_id: str
    quantity: typing.Optional[int]