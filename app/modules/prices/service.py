from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_session
from app.modules.goods.service import GoodsService
from app.modules.prices.entities import GoodVariationPriceEntity
from app.modules.prices.schemas.set_price import SetPriceSchema


class InvalidPriceError(ValueError):
    pass


class PricingService:
    def __init__(
        self,
        db: AsyncSession = Depends(get_session),
        goods_service: GoodsService = Depends(),
    ):
        self.db = db
        self.goods_service = goods_service

    async def set_price(self, data: SetPriceSchema):
        async with self.db.begin():
            now = datetime.now()

            good_variation = await self.goods_service.get_variation_by_id(
                data.variation_id
            )
            good_variation.latest_price = data.price
            good_variation.latest_price_date = now
            self.db.add(good_variation)

            self.db.add(
                GoodVariationPriceEntity(
                    good_variation=good_variation, price=data.price, date=now
                )
            )
