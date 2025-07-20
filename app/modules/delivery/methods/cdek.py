import typing as tp

import httpx

from app.core.config import settings
from app.modules.delivery.entities import CountryEntity
from app.modules.delivery.enums.countries import Countries
from app.modules.delivery.methods.base import BaseDeliveryMethod
from app.modules.delivery.schemas.create_order import CdekPackageItem, CdekPackage, CdekRecipient
from app.modules.delivery.schemas.get_cities import ListResponse, DeliveryPointFilter, CityFilter, CityResponse, \
    DeliveryPointResponse
from app.modules.goods.entities import GoodVariationEntity
from app.modules.orders.schemas.create import CreateOrderSchema
from app.modules.users.entities import UserEntity


class CDEKError(ValueError):
    pass


class CDEKDeliveryMethod(BaseDeliveryMethod):
    async def prepare_cdek_data(self, order_data: CreateOrderSchema, variations: tp.Dict[str, GoodVariationEntity],
                                order_id: str, current_user: UserEntity):
        package_items = []
        total_weight = 0

        for order_detail in order_data.details:
            variation_id = order_detail.variation_id
            variation = variations.get(variation_id, None)
            if variation is None:
                raise CDEKError('Unknown variation id')

            item = CdekPackageItem(
                ware_key=str(variation.id),
                name=variation.title,
                cost=variation.latest_price,
                weight=variation.weight,
                amount=order_detail.quantity,
                payment={
                    "value": variation.latest_price * order_detail.quantity,
                    "type": "CARD"
                }
            )
            package_items.append(item)
            total_weight += int(variation.weight * 1000 * order_detail.quantity)

        # Формируем посылку
        package = CdekPackage(
            number=f"PKG_{order_id}",
            weight=total_weight,
            length=0,
            width=0,
            height=0,
            items=package_items
        )

        delivery_point = await self.get_delivery_point(order_data.delivery_point)

        recipient = CdekRecipient(
            name=current_user.full_name,
            phones=[{"number": current_user.phone}]
        )

        body = {
            "type": 1,  # Тип заказа (1 - доставка)
            "number": str(order_id),
            "tariff_code": 139,  # Пример тарифа
            "from_location": {
                "code": 391,
                "city": "Балашиха",
                "address": "пр. Ласточкин, вл8, стр.8Б"
            },
            "to_location": {
                "code": delivery_point['code'],
                "city": delivery_point['city'],
                "address": delivery_point['address']
            },
            "packages": [package.model_dump()],
            "recipient": recipient.model_dump(),
            "delivery_recipient_cost": 350
        }

        if settings.CDEK_DEBUG:
            base_url = settings.CDEK_TEST_API_URL
        else:
            base_url = settings.CDEK_API_URL

        token = await self.get_cdek_auth_token()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{base_url}/orders",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json"
                    },
                    json=body

                )
                response.raise_for_status()
                data = response.json()
                return data

            except (httpx.HTTPStatusError, KeyError) as e:
                raise CDEKError(f"Ошибка при создании заказа в СДЕК: {str(e)}")

    async def get_delivery_point(self, code: str):

        token = self.get_cdek_auth_token()

        if settings.CDEK_DEBUG:
            base_url = settings.CDEK_TEST_API_URL
        else:
            base_url = settings.CDEK_API_URL

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{base_url}/deliverypoints",
                    params={"code": code},
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json"
                    }
                )
                response.raise_for_status()
                data = response.json()
                if not data or not isinstance(data, list):
                    raise CDEKError("Invalid response format from CDEK API")

                if len(data) == 0:
                    raise CDEKError(f"PVZ with code {code} not found")

                pvz = data[0]

                # Форматируем данные в единый словарь
                return {
                    "code": code,
                    "city": pvz.get("location", {}).get("city"),
                    "address": pvz.get("location", {}).get("address_full")
                }
            except (httpx.HTTPStatusError, KeyError) as e:
                raise CDEKError(f"Ошибка получения ПВЗ СДЕК: {str(e)}")




    def __init__(self):
        self.cdek_token_cache = None
        pass

    @staticmethod
    def _get_countries():
        return {
            Countries.RU: CountryEntity(name="Россия", code="RU"),
            Countries.BY: CountryEntity(name="Беларусь", code="BY"),
            Countries.KZ: CountryEntity(name="Казахстан", code="KZ")
        }

    async def get_cdek_auth_token(self):

        if self.cdek_token_cache:
            return self.cdek_token_cache

        if settings.CDEK_DEBUG:
            base_url = settings.CDEK_TEST_API_URL
            account = settings.CDEK_TEST_ACCOUNT
            secret = settings.CDEK_TEST_SECURE_PASSWORD
        else:
            base_url = settings.CDEK_API_URL
            account = settings.CDEK_ACCOUNT
            secret = settings.CDEK_SECURE_PASSWORD

        auth_url = f"{base_url}/oauth/token?grant_type=client_credentials&client_id={account}&client_secret={secret}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(auth_url)
                response.raise_for_status()
                token_data = response.json()
                cdek_token_cache = token_data["access_token"]
                self.cdek_token_cache = cdek_token_cache
                return cdek_token_cache
            except (httpx.HTTPStatusError, KeyError) as e:
                raise CDEKError(f"Ошибка авторизации в CDEK API: {str(e)}")

    async def get_countries(self):
        """
        Returns list of countries
        :return:
        """
        return [country.model_dump() for country in self._get_countries().values()]

    async def get_cities(self, filters: CityFilter):
        """
        Returns list of cities basing on provided country
        :return:
        """
        token = await self.get_cdek_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "country_codes": filters.country_code,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.CDEK_TEST_API_URL}/location/cities",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                cities = response.json()
                return ListResponse[CityResponse](data=cities, count=len(cities))
            except httpx.HTTPStatusError as e:
                raise CDEKError(
                    f"CDEK API error: {str(e)}"
                )

    async def get_addresses(self, filters: DeliveryPointFilter):
        """
        Returns list of addresses basing on provided city_code
        :return:
        """
        token = await self.get_cdek_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "city_code": str(filters.city_code),
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.CDEK_TEST_API_URL}/deliverypoints",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                points = response.json()
                return ListResponse[DeliveryPointResponse](data=points, count=len(points))
            except httpx.HTTPStatusError as e:
                raise CDEKError(
                    f"CDEK API error: {str(e)}"
                )

