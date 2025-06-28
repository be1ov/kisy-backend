import httpx

from app.core.config import settings
from app.modules.delivery.entities import DeliveryMethods, CDEKDeliveryMethod, BaseDeliveryMethod
from app.modules.delivery.schemas.get_cities import CityFilter, ListResponse, DeliveryPointFilter


class CDECError(ValueError):
    pass

class DeliveryService:
    def __init__(self):
        # Кэш для токена
        self.cdek_token_cache = None
        pass

    @staticmethod
    def get_delivery_method(method: DeliveryMethods) -> BaseDeliveryMethod:
        return {
            DeliveryMethods.CDEK: CDEKDeliveryMethod
        }[method]()

    async def get_cdek_auth_token(self):

        if self.cdek_token_cache:
            return self.cdek_token_cache

        auth_url = f"{settings.CDEK_TEST_API_URL}/oauth/token?grant_type=client_credentials&client_id={settings.CDEK_TEST_ACCOUNT}&client_secret={settings.CDEK_TEST_SECURE_PASSWORD}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(auth_url)
                response.raise_for_status()
                token_data = response.json()
                cdek_token_cache = token_data["access_token"]
                return cdek_token_cache
            except (httpx.HTTPStatusError, KeyError) as e:
                raise CDECError(f"Ошибка авторизации в CDEK API: {str(e)}")

    async def get_countries(self):
        """
        Returns list of countries basing on provided delivery method
        :return:
        """
        token = await self.get_cdek_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.CDEK_TEST_API_URL}/location/countries",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise CDECError(f"Ошибка CDEK API: {str(e)}")

    async def get_cities(self, filters: CityFilter):
        """
        Returns list of cities basing on provided delivery method and country
        :return:
        """
        token = await self.get_cdek_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {}

        if filters.country_code:
            if isinstance(filters.country_code, list):
                params["country_codes"] = ",".join(filters.country_code)
            else:
                params["country_codes"] = filters.country_code

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.CDEK_API_URL}/location/cities",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                cities = response.json()
                return ListResponse(data=cities, count=len(cities))
            except httpx.HTTPStatusError as e:
                raise CDECError(
                    f"CDEK API error: {str(e)}"
                )

    async def get_addresses(self, filters: DeliveryPointFilter):
        """
        Returns list of addresses basing on provided delivery method, country and city
        :return:
        """
        token = await self.get_cdek_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {}

        if filters.city_code:
            params["city_code"] = str(filters.city_code)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.CDEK_API_URL}/deliverypoints",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                points = response.json()
                return ListResponse(data=points, count=len(points))
            except httpx.HTTPStatusError as e:
                raise CDECError(
                    f"CDEK API error: {str(e)}"
                )
