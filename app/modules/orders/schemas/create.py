import typing as tp
from pydantic import BaseModel

from app.modules.delivery.enums.delivery_methods import DeliveryMethods


class OrderDetailSchema(BaseModel):
    variation_id: str
    quantity: int = 1

class CreateOrderSchema(BaseModel):
    delivery_method: DeliveryMethods
    delivery_point: str
    details: tp.List[OrderDetailSchema]
