import typing as tp
import datetime
import uuid
from typing import List

from sqlalchemy import String, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.session import Base
from app.modules.goods.entities import GoodVariationEntity
from app.modules.orders.schemas.order_schema import OrderDetailsSchema, OrderSchema
from app.modules.payments.enums.currencies import Currencies
from app.modules.users.entities import UserEntity
from app.modules.delivery.enums.delivery_methods import DeliveryMethods
from app.utils.date import format_date

if tp.TYPE_CHECKING:
    from app.modules.payments.entities import PaymentEntity


class OrderEntity(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    currency: Mapped[Currencies] = mapped_column(
        Enum(Currencies, name="currencies_enum", native_enum=False),
        nullable=False,
        default=Currencies.RUB,
    )

    user: Mapped["UserEntity"] = relationship()
    delivery_point: Mapped[str] = mapped_column(String, nullable=False)
    delivery_method: Mapped[DeliveryMethods] = mapped_column(
        Enum(DeliveryMethods, name="delivery-method", native_enum=False)
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(datetime.UTC),
    )

    cdek_order_uuid: Mapped[str] = mapped_column(String, nullable=True, default=None)

    @property
    def amount(self) -> float:
        return sum(details.amount for details in self.details)

    @property
    def description(self) -> str:
        return f"Заказ #{self.id} от {format_date(self.created_at)}"

    details: Mapped[list["OrderDetailsEntity"]] = relationship(
        back_populates="order", cascade="all", passive_deletes=True
    )

    payments: Mapped[List["PaymentEntity"]] = relationship(back_populates="order")

    def to_schema(self, fill_delivery_info: bool = False) -> OrderSchema:
        schema = OrderSchema(
            id=self.id,
            user_id=self.user_id,
            currency=self.currency,
            delivery_point=self.delivery_point,
            delivery_method=self.delivery_method,
            created_at=self.created_at.isoformat(),
            status=None,
            details=[detail.to_schema() for detail in self.details],
            amount=self.amount,
            track_number=self.cdek_order_uuid,
            delivery_info=None,
            tracking_info=None,
            delivery_point_info=None,
        )
        return schema


class OrderDetailsEntity(Base):
    __tablename__ = "order_details"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False)

    variation_id: Mapped[str] = mapped_column(
        ForeignKey("goods_variations.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Integer, nullable=False)

    order: Mapped["OrderEntity"] = relationship(back_populates="details")
    variation: Mapped["GoodVariationEntity"] = relationship()

    @property
    def amount(self) -> float:
        return self.quantity * self.price

    def to_schema(self) -> OrderDetailsSchema:
        return OrderDetailsSchema(
            variation=self.variation.to_schema(),
            quantity=self.quantity,
            price=self.price,
        )
