import typing as tp
from pydantic import BaseModel


class OrderDetailSchema(BaseModel):
    variation_id: str
    quantity: int = 1

class CreateOrderSchema(BaseModel):
    details: tp.List[OrderDetailSchema]