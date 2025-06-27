import abc
import uuid
from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.session import Base


class DeliveryMethods(str, Enum):
    CDEK = "cdek"


class BaseDeliveryMethod:
    @abc.abstractmethod
    def get_cities(self):
        pass


class CDEKDeliveryMethod(BaseDeliveryMethod):
    def get_cities(self):
        pass
