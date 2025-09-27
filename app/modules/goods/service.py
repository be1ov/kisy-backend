from typing import Sequence
import uuid

import aiofiles
from fastapi import Depends, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.session import get_session
from app.modules.goods.entities import (
    GoodEntity,
    GoodVariationEntity,
    GoodVariationPhotoEntity,
)
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
        return result.scalars().one_or_none()

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

    async def upload_photos(
        self, variation_id: str, file: UploadFile
    ) -> GoodVariationEntity:
        async with self.db.begin():
            stmt = (
                select(GoodVariationEntity)
                .where(GoodVariationEntity.id == variation_id)
                .options(selectinload(GoodVariationEntity.photos))
            )
            result = await self.db.execute(stmt)
            variation = result.scalars().one_or_none()
            if variation is None:
                raise ValueError("Variation not found")

            file_content = await file.read()
            content_type = file.content_type
            if not content_type or content_type not in ["image/jpeg", "image/png"]:
                raise ValueError("File must be an image")

            extension = content_type.split("/")[-1] if "/" in content_type else "jpg"

            url = f"/static/goods/{variation_id}/{uuid.uuid4()}_{file.filename}.{extension}"
            async with aiofiles.open(f".{url}", "wb") as out_file:
                await out_file.write(file_content)

            photo = GoodVariationPhotoEntity(url=url, is_main=False)
            variation.photos.append(photo)

            self.db.add(variation)

        return variation
