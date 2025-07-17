import uuid
import typing as tp

import httpx
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.testing.pickleable import Order

from app.core.config import settings
from app.core.db.session import get_session
from app.modules.delivery.service import DeliveryService
from app.modules.goods.entities import GoodVariationEntity
from app.modules.orders.entities import OrderEntity, OrderDetailsEntity
from app.modules.orders.schemas.create import CreateOrderSchema
from app.modules.users.entities import UserEntity


class OrderCreationError(ValueError):
    pass


class UndefinedOrder(ValueError):
    pass


class OrderService:
    def __init__(self, db: AsyncSession = Depends(get_session), delivery_service: DeliveryService = Depends()):
        self.db = db
        self.delivery_service = delivery_service


    async def create_order(self, order_data: CreateOrderSchema, current_user: UserEntity):

        variation_ids = [detail.variation_id for detail in order_data.details]

        stmt = select(GoodVariationEntity).where(
            GoodVariationEntity.id.in_(variation_ids)
        )
        result = await self.db.execute(stmt)
        found_variations = result.scalars().all()

        found_variation_ids = {v.id for v in found_variations}
        for detail in order_data.details:
            if detail.variation_id not in found_variation_ids:
                raise OrderCreationError("Goods variations not found")

        variation_map = {v.id: v for v in found_variations}
        for detail in order_data.details:
            variation = variation_map[detail.variation_id]
            if variation.latest_price is None:
                raise OrderCreationError(f"Variation {variation.id} has no latest price set")

        order = OrderEntity(
            user_id=current_user.id,
            delivery_point = order_data.delivery_point,
            delivery_method = order_data.delivery_method,
        )
        self.db.add(order)

        for detail in order_data.details:
            variation = variation_map[detail.variation_id]
            order_detail = OrderDetailsEntity(
                order=order,
                variation=variation,
                quantity=detail.quantity,
                price=variation.latest_price
            )
            self.db.add(order_detail)

        await self.db.commit()
        await self.db.refresh(order)

        cdek_data = await self.delivery_service.prepare_cdek_data(order_data, variation_map, order.id, current_user)

        result = {
            "order": order,
            "cdek_data": cdek_data,
        }
        return result

    async def get_by_id(self, order_id: str) -> OrderEntity:
        """
        Returns order by its id.

        If there is no order with provided id, raises UndefinedOrder

        :param order_id: Order id
        :return:
        """
        stmt = select(OrderEntity).options(
            selectinload(OrderEntity.user),
            selectinload(OrderEntity.payments),
            selectinload(OrderEntity.details).selectinload(OrderDetailsEntity.variation)
        ).where(OrderEntity.id == order_id)
        result = await self.db.execute(stmt)
        order = result.scalars().first()
        if not order:
            raise UndefinedOrder("Order not found")

        return order
