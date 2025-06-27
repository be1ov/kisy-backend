from app.modules.delivery.entities import DeliveryMethods, CDEKDeliveryMethod, BaseDeliveryMethod


class DeliveryService:
    def __init__(self):
        pass

    @staticmethod
    def get_delivery_method(method: DeliveryMethods) -> BaseDeliveryMethod:
        return {
            DeliveryMethods.CDEK: CDEKDeliveryMethod
        }[method]()

    async def get_cities(self, data: ):