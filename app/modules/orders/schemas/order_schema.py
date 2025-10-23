import typing as tp
from pydantic import BaseModel
from app.modules.goods.schemas.good_variation_schema import GoodVariationSchema
from app.modules.delivery.schemas.delivery_info import (
    DeliveryInfo,
    TrackingInfo,
    DeliveryPoint,
)


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
    track_number: tp.Optional[str] = None

    # Новые поля для расширенной информации о доставке
    delivery_info: tp.Optional[DeliveryInfo] = None
    tracking_info: tp.Optional[TrackingInfo] = None
    delivery_point_info: tp.Optional[DeliveryPoint] = None
