from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.session import get_session
from app.modules.lk.schemas.responses.lk_data_response_schema import (
    LKDataResponseSchema,
)
from app.modules.orders.service import OrderService
from app.modules.users.entities import UserEntity


class LKService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_session),
        orders_service: OrderService = Depends(),
    ):
        self.db = db
        self.orders_service = orders_service

    async def get_info(self, user: UserEntity) -> LKDataResponseSchema:
        orders = await self.orders_service.get_orders_by_user(user)
        return LKDataResponseSchema(
            user=user.to_schema(), orders=[order.to_schema() for order in orders]
        )
