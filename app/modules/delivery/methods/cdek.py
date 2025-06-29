import httpx

from app.core.config import settings
from app.modules.delivery.entities import CountryEntity
from app.modules.delivery.enums.countries import Countries
from app.modules.delivery.methods.base import BaseDeliveryMethod
from app.modules.delivery.schemas.get_cities import ListResponse, DeliveryPointFilter, CityFilter, CityResponse, \
    DeliveryPointResponse


class CDEKError(ValueError):
    pass


class CDEKDeliveryMethod(BaseDeliveryMethod):
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

        auth_url = f"{settings.CDEK_TEST_API_URL}/oauth/token?grant_type=client_credentials&client_id={settings.CDEK_TEST_ACCOUNT}&client_secret={settings.CDEK_TEST_SECURE_PASSWORD}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(auth_url)
                response.raise_for_status()
                token_data = response.json()
                print(token_data)
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
        print(headers)
        params = {
            "country_codes": filters.country_code,
        }
        print(params)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.CDEK_TEST_API_URL}/location/cities",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                cities = response.json()
                print(cities)
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
