import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Integer
from sqlalchemy.orm import mapped_column, Mapped

from app.core.db.session import Base


class UserEntity(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    birth_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, default="", server_default="")

    signup_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
