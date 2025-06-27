import uuid

from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.session import Base
from app.modules.goods.entities import GoodVariationEntity
from app.modules.users.entities import UserEntity


class GoodsInCart(Base):
    __tablename__ = 'goods_in_cart'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    variation_id: Mapped[str] = mapped_column(ForeignKey('goods_variations.id', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, default=1)

    variation: Mapped["GoodVariationEntity"] = relationship()
    user: Mapped["UserEntity"] = relationship()