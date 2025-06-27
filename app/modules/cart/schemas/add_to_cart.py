import typing as tp

from pydantic import BaseModel


class AddToCartSchema(BaseModel):
    variation_id: str
    quantity: tp.Optional[int]