import uuid
import datetime

from sqlalchemy import String, ForeignKey, Boolean, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.session import Base


class GoodEntity(Base):
    __tablename__ = 'goods'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

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

    good: Mapped["GoodEntity"] = relationship(back_populates="variations")
    photos: Mapped[list["GoodVariationPhotoEntity"]] = relationship(
        back_populates="variation",
        cascade="all, delete-orphan",
    )


class GoodVariationPhotoEntity(Base):
    __tablename__ = 'goods_variation_photos'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    variation_id: Mapped[str] = mapped_column(ForeignKey('goods_variations.id', ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String)
    is_main: Mapped[str] = mapped_column(Boolean)

    variation: Mapped["GoodVariationEntity"] = relationship(back_populates="photos")
