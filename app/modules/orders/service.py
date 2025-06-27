import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_session
from app.modules.goods.entities import GoodVariationEntity
from app.modules.orders.entities import OrderEntity, OrderDetailsEntity
from app.modules.orders.schemas.create import CreateOrderSchema
from app.modules.users.entities import UserEntity


class OrderCreationError(ValueError):
    pass

class OrderService:
    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def create_order(self, order_data: CreateOrderSchema, current_user: UserEntity):

        variation_ids = [detail.variation_id for detail in order_data.details]

        stmt = select(GoodVariationEntity).where(
            GoodVariationEntity.id.in_(variation_ids)
        )
        result = await self.db.execute(stmt)
        found_variations = result.scalars().all()

        # Проверяем, что все варианты найдены
        found_variation_ids = {v.id for v in found_variations}
        for detail in order_data.details:
            if detail.variation_id not in found_variation_ids:
                raise OrderCreationError("Goods variations not found")

        # Проверяем наличие цен у всех вариантов
        variation_map = {v.id: v for v in found_variations}
        for detail in order_data.details:
            variation = variation_map[detail.variation_id]
            if variation.latest_price is None:
                raise OrderCreationError(f"Variation {variation.id} has no latest price set")

        # Создаем заказ
        order = OrderEntity(
            user_id=current_user.id,
        )
        self.db.add(order)

        # 7. Создаем детали заказа
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

        return order