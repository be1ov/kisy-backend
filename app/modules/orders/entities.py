import typing as tp
import datetime
import uuid
from typing import List

from sqlalchemy import String, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.session import Base
from app.modules.goods.entities import GoodVariationEntity
from app.modules.payments.enums.currencies import Currencies
from app.modules.users.entities import UserEntity
from app.modules.delivery.enums.delivery_methods import DeliveryMethods

if tp.TYPE_CHECKING:
    from app.modules.payments.entities import PaymentEntity


class OrderEntity(Base):
    __tablename__ = 'orders'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), nullable=False)
    currency: Mapped[Currencies] = mapped_column(Enum(Currencies, name="currencies_enum", native_enum=False), nullable=False, default=Currencies.RUB)

    user: Mapped["UserEntity"] = relationship()
    delivery_point: Mapped[str] = mapped_column(String, nullable=False)
    delivery_method: Mapped[DeliveryMethods] = mapped_column(Enum(DeliveryMethods, name="delivery-method", native_enum=False))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.datetime.now(datetime.UTC))

    @property
    def amount(self) -> float:
        return sum(details.amount for details in self.details)

    @property
    def description(self) -> str:
        return f"Заказ #{self.id} от {self.created_at}"

    details: Mapped[list["OrderDetailsEntity"]] = relationship(
        back_populates="order",
        cascade="all",
        passive_deletes=True
    )

    payments: Mapped[List["PaymentEntity"]] = relationship(back_populates="order")


class OrderDetailsEntity(Base):
    __tablename__ = 'order_details'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), nullable=False)

    variation_id: Mapped[str] = mapped_column(ForeignKey('goods_variations.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Integer, nullable=False)

    order: Mapped["OrderEntity"] = relationship(back_populates="details")
    variation: Mapped["GoodVariationEntity"] = relationship()

    @property
    def amount(self) -> float:
        return self.quantity * self.price