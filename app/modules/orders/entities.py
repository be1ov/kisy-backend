import datetime
import uuid
from datetime import timezone

from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.session import Base
from app.modules.goods.entities import GoodVariationEntity
from app.modules.users.entities import UserEntity


class OrderEntity(Base):
    __tablename__ = 'orders'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), nullable=False)

    user: Mapped["UserEntity"] = relationship()
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False, default=datetime.datetime.now(timezone.utc))

    details: Mapped[list["OrderDetailsEntity"]] = relationship(
        back_populates="order",
        cascade="all",
        passive_deletes=True
    )

class OrderDetailsEntity(Base):
    __tablename__ = 'order_details'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), nullable=False)

    variation_id: Mapped[str] = mapped_column(ForeignKey('goods_variations.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Integer, nullable=False)

    order: Mapped["OrderEntity"] = relationship(back_populates="details")
    variation: Mapped["GoodVariationEntity"] = relationship()