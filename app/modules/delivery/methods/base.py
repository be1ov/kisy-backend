import abc

from app.modules.delivery.schemas.get_cities import CityFilter, DeliveryPointFilter


class BaseDeliveryMethod:
    @abc.abstractmethod
    async def get_cities(self, filter: CityFilter):
        pass

    @abc.abstractmethod
    async def get_countries(self):
        pass

    @abc.abstractmethod
    async def get_addresses(self, filter: DeliveryPointFilter):
        pass
