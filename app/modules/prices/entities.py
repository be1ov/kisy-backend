import datetime
import uuid

from sqlalchemy import String, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.session import Base
from app.modules.goods.entities import GoodVariationEntity


class GoodVariationPriceEntity(Base):
    __tablename__ = 'good_variation_price'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date: Mapped[datetime] = mapped_column(DateTime)
    good_variation_id: Mapped[str] = mapped_column(ForeignKey('goods_variations.id'), nullable=False)

    good_variation: Mapped["GoodVariationEntity"] = relationship(foreign_keys=[good_variation_id])
    price: Mapped[float] = mapped_column(Float, default=0)
