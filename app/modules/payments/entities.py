import uuid

from pydantic import BaseModel
from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.session import Base
from app.modules.orders.entities import OrderEntity
from app.modules.payments.enums.payment_methods import PaymentMethods
from app.modules.payments.enums.payment_statuses import PaymentStatuses


class PaymentMethodEntity(BaseModel):
    name: str
    code: PaymentMethods


class PaymentEntity(Base):
    __tablename__ = 'payments'
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    order_id: Mapped[str] = mapped_column(ForeignKey('orders.id'), nullable=False)
    link: Mapped[str] = mapped_column(String, nullable=True)
    method: Mapped[PaymentMethods] = mapped_column(Enum(PaymentMethods, name="payment_types_enum"), nullable=False)
    status: Mapped[str] = mapped_column(Enum(PaymentStatuses, name="payment_types_enum"), nullable=False,
                                        default=PaymentStatuses.CREATED)
    
    order: Mapped[OrderEntity] = relationship(back_populates="payments")
