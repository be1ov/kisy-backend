import uuid
import datetime

from sqlalchemy import String, ForeignKey, Boolean, Float, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.session import Base
from app.modules.goods.enums.vat_rates import VATRate


class GoodEntity(Base):
    __tablename__ = 'goods'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    vat_rate: Mapped[VATRate] = mapped_column(Enum(VATRate, name="vat_rate", native_enum=False), default=VATRate.VAT_20)

    variations: Mapped[list["GoodVariationEntity"]] = relationship(
        back_populates="good",
        cascade="all",
        passive_deletes=True
    )

    def __str__(self):
        return self.title


class GoodVariationEntity(Base):
    __tablename__ = 'goods_variations'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    good_id: Mapped[str] = mapped_column(ForeignKey('goods.id', ondelete="RESTRICT"))

    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    latest_price: Mapped[float] = mapped_column(Float, nullable=True, default=None)
    latest_price_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)

    weight: Mapped[float] = mapped_column(Float, nullable=True, default=0)
    length: Mapped[float] = mapped_column(Float, nullable=True, default=0)
    width: Mapped[float] = mapped_column(Float, nullable=True, default=0)
    height: Mapped[float] = mapped_column(Float, nullable=True, default=0)

    good: Mapped["GoodEntity"] = relationship(back_populates="variations")
    photos: Mapped[list["GoodVariationPhotoEntity"]] = relationship(
        back_populates="variation",
        cascade="all, delete-orphan",
    )

    def __str__(self):
        return self.title

    @property
    def receipt_description(self) -> str:
        if self.title == self.good.title:
            return self.title

        return f"{self.good.title} / {self.title}"



class GoodVariationPhotoEntity(Base):
    __tablename__ = 'goods_variation_photos'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    variation_id: Mapped[str] = mapped_column(ForeignKey('goods_variations.id', ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String)
    is_main: Mapped[bool] = mapped_column(Boolean)

    variation: Mapped["GoodVariationEntity"] = relationship(back_populates="photos")

    def __str__(self):
        return f"{self.variation.title} ({self.id[-4:]})"
