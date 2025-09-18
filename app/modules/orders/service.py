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
from app.modules.delivery.enums.delivery_statuses import DeliveryStatusesEnum
from app.modules.delivery.service import DeliveryService
from app.modules.goods.entities import GoodVariationEntity
from app.modules.orders.entities import OrderEntity, OrderDetailsEntity
from app.modules.orders.schemas.create import CreateOrderSchema
from app.modules.users.entities import UserEntity
from app.modules.cart.service import CartService


class OrderCreationError(ValueError):
    pass


class UndefinedOrder(ValueError):
    pass


class OrderService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_session),
        delivery_service: DeliveryService = Depends(),
        cart_service: CartService = Depends(),
    ):
        self.db = db
        self.delivery_service = delivery_service
        self.cart_service = cart_service

    async def create_order(
        self, order_data: CreateOrderSchema, current_user: UserEntity
    ):

        variation_ids = [detail.variation_id for detail in order_data.details]

        stmt = select(GoodVariationEntity).where(
            GoodVariationEntity.id.in_(variation_ids)
        )
        result = await self.db.execute(stmt)
        found_variations = result.scalars().all()

        variation_map = {v.id: v.__dict__ for v in found_variations}
        for detail in order_data.details:
            if variation_map.get(detail.variation_id, None) is None:
                raise OrderCreationError("Goods variations not found")

            variation = variation_map[detail.variation_id]
            if variation["latest_price"] is None:
                raise OrderCreationError(
                    f"Variation {variation['id']} has no latest price set"
                )

        order = OrderEntity(
            user_id=current_user.id,
            delivery_point=order_data.delivery_point,
            delivery_method=order_data.delivery_method,
        )
        self.db.add(order)

        for detail in order_data.details:
            variation = variation_map[detail.variation_id]
            order_detail = OrderDetailsEntity(
                order=order,
                variation_id=variation["id"],
                quantity=detail.quantity,
                price=variation["latest_price"],
            )
            self.db.add(order_detail)

        await self.db.flush()

        # cdek_data = await self.delivery_service.prepare_cdek_data(order_data, variation_map, order.id, current_user)
        await self.db.commit()
        await self.db.refresh(order)

        await self.cart_service.clear_cart(current_user)

        result = {
            "order": order
            # "cdek_data": cdek_data,
        }
        return result

    async def get_by_id(self, order_id: str) -> OrderEntity:
        """
        Returns order by its id.

        If there is no order with provided id, raises UndefinedOrder

        :param order_id: Order id
        :return:
        """
        stmt = (
            select(OrderEntity)
            .options(
                selectinload(OrderEntity.user),
                selectinload(OrderEntity.payments),
                selectinload(OrderEntity.details).selectinload(
                    OrderDetailsEntity.variation
                ),
            )
            .where(OrderEntity.id == order_id)
        )
        result = await self.db.execute(stmt)
        order = result.scalars().first()
        if not order:
            raise UndefinedOrder("Order not found")

        return order

    async def get_status(self, order: OrderEntity) -> tp.Optional[DeliveryStatusesEnum]:
        status = await self.delivery_service.get_order_status(order)
        return status if status else None

    async def get_orders_by_user(self, user: UserEntity) -> tp.List[OrderEntity]:
        stmt = (
            select(OrderEntity)
            .options(
                selectinload(OrderEntity.user),
                selectinload(OrderEntity.payments),
                selectinload(OrderEntity.details).selectinload(
                    OrderDetailsEntity.variation
                ),
            )
            .where(OrderEntity.user_id == user.id)
            .order_by(OrderEntity.created_at.desc())
        )
        result = await self.db.execute(stmt)
        orders = result.scalars().all()
        return list(orders)
