import typing as tp
from pydantic import BaseModel


class OrderDetailsSchema(BaseModel):
    variation: tp.Dict[str, tp.Any]
    quantity: int
    price: float


class OrderSchema(BaseModel):
    id: str
    user_id: str
    currency: str
    delivery_point: str
    delivery_method: str
    created_at: str
    status: tp.Optional[str] = None
    details: tp.Optional[tp.List[tp.Dict[str, tp.Any]]] = []
    amount: float
