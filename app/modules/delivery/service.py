from app.modules.delivery.entities import DeliveryMethods, CDEKDeliveryMethod, BaseDeliveryMethod


class DeliveryService:
    def __init__(self):
        pass

    @staticmethod
    def get_delivery_method(method: DeliveryMethods) -> BaseDeliveryMethod:
        return {
            DeliveryMethods.CDEK: CDEKDeliveryMethod
        }[method]()

    async def get_countries(self):
        """
        Returns list of countries basing on provided delivery method
        :return:
        """
        pass

    async def get_cities(self):
        """
        Returns list of cities basing on provided delivery method and country
        :return:
        """
        pass

    async def get_addresses(self):
        """
        Returns list of adresses basing on provided delivery method, country and city
        :return:
        """
        pass
