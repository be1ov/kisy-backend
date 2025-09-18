import typing as tp
from pydantic import BaseModel

from app.modules.orders.schemas.order_schema import OrderSchema
from app.modules.users.schema.user_schema import UserSchema


class LKDataResponseSchema(BaseModel):
    user: UserSchema
    orders: tp.List[OrderSchema] = []
