from typing import Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.session import get_session
from app.modules.goods.entities import GoodEntity, GoodVariationEntity
from app.modules.goods.schemas.create import CreateGoodSchema


class GoodsService:
    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def get_by_id(self, _id: str) -> GoodEntity:
        stmt = (
            select(GoodEntity)
            .where(GoodEntity.id == _id)
            .options(
                selectinload(GoodEntity.variations).selectinload(
                    GoodVariationEntity.photos
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar()

    async def get_variation_by_id(self, _id: str) -> GoodVariationEntity:
        stmt = (
            select(GoodVariationEntity)
            .options(selectinload(GoodVariationEntity.photos))
            .where(GoodVariationEntity.id == _id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_goods_paginated(
        self, page: int = 1, size: int = 10
    ) -> Sequence[GoodEntity]:
        stmt = (
            select(GoodEntity)
            .offset((page - 1) * size)
            .limit(size)
            .options(
                selectinload(GoodEntity.variations).selectinload(
                    GoodVariationEntity.photos
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, data: CreateGoodSchema):
        async with self.db.begin():
            good = GoodEntity(
                title=data.title,
                description=data.description,
            )
            self.db.add(good)

            variation = GoodVariationEntity(
                good=good,
                title=data.title,
                description=data.description,
            )
            self.db.add(variation)

        return good

    async def create_variation(self, good_id: str, data: CreateGoodSchema):
        async with self.db.begin():
            variation = GoodVariationEntity(
                good_id=good_id,
                title=data.title,
                description=data.description,
            )
            self.db.add(variation)

        return variation
