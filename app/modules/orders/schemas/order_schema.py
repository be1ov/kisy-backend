import typing as tp
from pydantic import BaseModel
from app.modules.goods.schemas.good_variation_schema import GoodVariationSchema


class OrderDetailsSchema(BaseModel):
    variation: GoodVariationSchema
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
    details: tp.List[OrderDetailsSchema] = []
    amount: float
