from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.session import get_session
from app.modules.cart.entities import GoodsInCart
from app.modules.goods.entities import GoodVariationEntity
from app.modules.users.entities import UserEntity


class NoSuchItem(ValueError):
    pass

class CartService:
    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def add_to_cart(self, user: UserEntity, variation: GoodVariationEntity, quantity: int = 1):
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        stmt = select(GoodsInCart).where(
            GoodsInCart.user == user,
            GoodsInCart.variation == variation
        )
        result = await self.db.execute(stmt)
        cart_item = result.scalars().first()

        if cart_item is None:
            cart_item = GoodsInCart(user=user, variation=variation, quantity=quantity)
        else:
            cart_item.quantity += quantity

        self.db.add(cart_item)
        await self.db.commit()
        return cart_item

    async def delete_from_cart(self, user: UserEntity, variation: GoodVariationEntity, quantity: int = 1):
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        stmt = select(GoodsInCart).where(
            GoodsInCart.user == user,
            GoodsInCart.variation == variation
        )
        result = await self.db.execute(stmt)
        cart_item = result.scalars().first()

        if cart_item is None:
            raise NoSuchItem()

        deleted = False

        if cart_item.quantity > quantity:
            cart_item.quantity -= quantity
            self.db.add(cart_item)
        else:
            await self.db.delete(cart_item)
            deleted = True

        await self.db.commit()
        return None if deleted else cart_item

    async def get(self, user: UserEntity):
        stmt = (
            select(GoodsInCart)
            .where(GoodsInCart.user == user)
            .options(
                selectinload(GoodsInCart.variation)
                .selectinload(GoodVariationEntity.photos),
                selectinload(GoodsInCart.variation)
                .selectinload(GoodVariationEntity.good)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def clear_cart(self, user: UserEntity):
        stmt = (
            delete(GoodsInCart)
            .where(GoodsInCart.user == user)
        )
        await session.execute(stmt)
        await session.commit()
