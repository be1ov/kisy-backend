import typing as tp

import httpx

from app.core.config import settings
from app.modules.delivery.entities import CountryEntity
from app.modules.delivery.enums.countries import Countries
from app.modules.delivery.enums.delivery_statuses import DeliveryStatusesEnum
from app.modules.delivery.methods.base import BaseDeliveryMethod
from app.modules.delivery.schemas.create_order import (
    CdekPackageItem,
    CdekPackage,
    CdekRecipient,
)
from app.modules.delivery.schemas.delivery_info import (
    DeliveryInfo,
    TrackingInfo,
    DeliveryPoint,
)
from app.modules.delivery.schemas.get_cities import (
    ListResponse,
    DeliveryPointFilter,
    CityFilter,
    CityResponse,
    DeliveryPointResponse,
)
from app.modules.goods.entities import GoodVariationEntity
from app.modules.orders.entities import OrderEntity
from app.modules.orders.schemas.create import CreateOrderSchema
from app.modules.orders.schemas.order_schema import OrderSchema
from app.modules.users.entities import UserEntity


class CDEKError(ValueError):
    pass


class CDEKDeliveryMethod(BaseDeliveryMethod):
    async def prepare_cdek_data(
        self, order_data: OrderEntity, order_id: str, current_user: UserEntity
    ):
        package_items = []
        total_weight = 0

        for order_detail in order_data.details:
            variation = order_detail.variation
            # variation = variations.get(variation_id, None)
            if variation is None:
                raise CDEKError("Unknown variation id")

            item = CdekPackageItem(
                ware_key=str(variation.id),
                name=variation.title,
                cost=variation.latest_price,
                weight=variation.weight,
                amount=int(order_detail.quantity),
                payment={
                    "value": variation.latest_price * order_detail.quantity,
                    "type": "CARD",
                },
            )
            package_items.append(item)
            total_weight += int(variation.weight * 1000 * order_detail.quantity)

        # Формируем посылку
        package = CdekPackage(
            number=f"PKG_{order_id}",
            weight=total_weight,
            length=1,
            width=1,
            height=1,
            items=package_items,
        )

        delivery_point = await self.get_delivery_point(order_data.delivery_point)

        recipient = CdekRecipient(
            name=current_user.full_name, phones=[{"number": current_user.phone}]
        )

        body = {
            "type": 1,
            "number": str(order_id),
            "tariff_code": 139,
            "from_location": {
                "code": 391,
                "city": "Балашиха",
                "address": "пр. Ласточкин, вл8, стр.8Б",
            },
            "to_location": {
                "code": delivery_point["code"],
                "city": delivery_point["city"],
                "address": delivery_point["address"],
            },
            "packages": [package.model_dump()],
            "recipient": recipient.model_dump(),
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
                        "Accept": "application/json",
                    },
                    json=body,
                )
                response.raise_for_status()
                data = response.json()

                cdek_entity = data.get("entity", None)
                if cdek_entity is None:
                    raise CDEKError("CDEK entity not found in response")

                cdek_uuid = cdek_entity.get("uuid", None)
                if cdek_uuid is None:
                    raise CDEKError("CDEK UUID not found in response")
                order_data.cdek_order_uuid = cdek_uuid

                return data
            except (httpx.HTTPStatusError, KeyError) as e:
                raise CDEKError(f"Ошибка при создании заказа в СДЕК: {str(e)}")

    async def get_delivery_point(self, code: str):

        token = await self.get_cdek_auth_token()
        print(token)

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
                        "Accept": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()
                if not data or not isinstance(data, list):
                    raise CDEKError("Invalid response format from CDEK API")

                if len(data) == 0:
                    raise CDEKError(f"PVZ with code {code} not found")

                pvz = data[0]

                return {
                    "code": pvz.get("location", {}).get("city_code"),
                    "city": pvz.get("location", {}).get("city"),
                    "address": pvz.get("location", {}).get("address_full"),
                }
            except (httpx.HTTPStatusError, KeyError) as e:
                raise CDEKError(f"Ошибка получения ПВЗ СДЕК: {str(e)}")

    @staticmethod
    def _get_countries():
        return {
            Countries.RU: CountryEntity(name="Россия", code="RU"),
            Countries.BY: CountryEntity(name="Беларусь", code="BY"),
            Countries.KZ: CountryEntity(name="Казахстан", code="KZ"),
        }

    async def get_cdek_auth_token(self):
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
            except (httpx.HTTPStatusError, KeyError) as e:
                raise CDEKError(f"Ошибка авторизации в CDEK API: {str(e)}")

        return token_data["access_token"]

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

        if settings.CDEK_DEBUG:
            base_url = settings.CDEK_TEST_API_URL
        else:
            base_url = settings.CDEK_API_URL

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{base_url}/location/cities", headers=headers, params=params
                )
                response.raise_for_status()
                cities = response.json()
                return ListResponse[CityResponse](data=cities, count=len(cities))
            except httpx.HTTPStatusError as e:
                raise CDEKError(f"CDEK API error: {str(e)}")

    async def get_addresses(self, filters: DeliveryPointFilter):
        """
        Returns list of addresses basing on provided city_code
        :return:
        """
        if settings.CDEK_DEBUG:
            base_url = settings.CDEK_TEST_API_URL
        else:
            base_url = settings.CDEK_API_URL

        token = await self.get_cdek_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "city_code": str(filters.city_code),
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{base_url}/deliverypoints", headers=headers, params=params
                )
                response.raise_for_status()
                points = response.json()
                return ListResponse[DeliveryPointResponse](
                    data=points, count=len(points)
                )
            except httpx.HTTPStatusError as e:
                raise CDEKError(f"CDEK API error: {str(e)}")

    async def map_delivery_status(self, status: str) -> DeliveryStatusesEnum:
        mapping = {
            # Заказ создан, но требует валидации
            "ACCEPTED": DeliveryStatusesEnum.CREATED,
            # Заказ создан и прошел валидации
            "CREATED": DeliveryStatusesEnum.CREATED,
            # Принят на склад отправителя
            "RECEIVED_AT_SHIPMENT_WAREHOUSE": DeliveryStatusesEnum.IN_PROGRESS,
            # Выдан на отправку в г. отправителе
            "READY_TO_SHIP_AT_SENDING_OFFICE": DeliveryStatusesEnum.IN_PROGRESS,
            "READY_FOR_SHIPMENT_IN_TRANSIT_CITY": DeliveryStatusesEnum.IN_PROGRESS,
            # Готов к отправке в г. отправителе
            "READY_FOR_SHIPMENT_IN_SENDER_CITY": DeliveryStatusesEnum.IN_PROGRESS,
            # Возвращен на склад отправителя
            "RETURNED_TO_SENDER_CITY_WAREHOUSE": DeliveryStatusesEnum.IN_PROGRESS,
            # Сдан перевозчику в г. отправителе
            "TAKEN_BY_TRANSPORTER_FROM_SENDER_CITY": DeliveryStatusesEnum.IN_PROGRESS,
            # Отправлен в г. транзит
            "SENT_TO_TRANSIT_CITY": DeliveryStatusesEnum.IN_PROGRESS,
            # Встречен в г. транзите
            "ACCEPTED_IN_TRANSIT_CITY": DeliveryStatusesEnum.IN_PROGRESS,
            # Принят на склад транзита
            "ACCEPTED_AT_TRANSIT_WAREHOUSE": DeliveryStatusesEnum.IN_PROGRESS,
            # Возвращен на склад транзита
            "RETURNED_TO_TRANSIT_WAREHOUSE": DeliveryStatusesEnum.IN_PROGRESS,
            # Выдан на отправку в г. транзите
            "READY_TO_SHIP_IN_TRANSIT_OFFICE": DeliveryStatusesEnum.IN_PROGRESS,
            # Сдан перевозчику в г. транзите
            "TAKEN_BY_TRANSPORTER_FROM_TRANSIT_CITY": DeliveryStatusesEnum.IN_PROGRESS,
            # Отправлен в г. отправитель
            "SENT_TO_SENDER_CITY": DeliveryStatusesEnum.IN_PROGRESS,
            # Отправлен в г. получатель
            "SENT_TO_RECIPIENT_CITY": DeliveryStatusesEnum.IN_PROGRESS,
            # Встречен в г. отправителе
            "ACCEPTED_IN_SENDER_CITY": DeliveryStatusesEnum.IN_PROGRESS,
            # Встречен в г. получателе
            "ACCEPTED_IN_RECIPIENT_CITY": DeliveryStatusesEnum.IN_PROGRESS,
            # Принят на склад доставки
            "ACCEPTED_AT_RECIPIENT_CITY_WAREHOUSE": DeliveryStatusesEnum.IN_PROGRESS,
            # Принят на склад до востребования
            "ACCEPTED_AT_PICK_UP_POINT": DeliveryStatusesEnum.IN_PROGRESS,
            # Выдан на доставку
            "TAKEN_BY_COURIER": DeliveryStatusesEnum.IN_PROGRESS,
            # Возвращен на склад доставки
            "RETURNED_TO_RECIPIENT_CITY_WAREHOUSE": DeliveryStatusesEnum.IN_PROGRESS,
            # Вручен
            "DELIVERED": DeliveryStatusesEnum.DELIVERED,
            # Не вручен
            "NOT_DELIVERED": DeliveryStatusesEnum.CANCELLED,
            # Некорректный заказ
            "INVALID": DeliveryStatusesEnum.CANCELLED,
            # Таможенное оформление в стране отправления
            "IN_CUSTOMS_INTERNATIONAL": DeliveryStatusesEnum.IN_PROGRESS,
            # Отправлено в страну назначения
            "SHIPPED_TO_DESTINATION": DeliveryStatusesEnum.SHIPPED,
            # Передано транзитному перевозчику
            "PASSED_TO_TRANSIT_CARRIER": DeliveryStatusesEnum.SHIPPED,
            # Таможенное оформление в стране назначения
            "IN_CUSTOMS_LOCAL": DeliveryStatusesEnum.IN_PROGRESS,
            # Таможенное оформление завершено
            "CUSTOMS_COMPLETE": DeliveryStatusesEnum.IN_PROGRESS,
            # Заложен в постамат
            "POSTOMAT_POSTED": DeliveryStatusesEnum.IN_PROGRESS,
            # Изъят из постамата курьером
            "POSTOMAT_SEIZED": DeliveryStatusesEnum.CANCELLED,
            # Изъят из постамата клиентом
            "POSTOMAT_RECEIVED": DeliveryStatusesEnum.DELIVERED,
            # Удален/отменен
            "REMOVED": DeliveryStatusesEnum.CANCELLED,
        }

        # По умолчанию - ожидает оплаты, если статус неизвестен
        return mapping.get(status, DeliveryStatusesEnum.WAITING_FOR_PAYMENT)

    async def get_status(self, order: OrderSchema) -> DeliveryStatusesEnum:
        if not order.track_number:
            return DeliveryStatusesEnum.WAITING_FOR_PAYMENT

        token = await self.get_cdek_auth_token()

        if settings.CDEK_DEBUG:
            base_url = settings.CDEK_TEST_API_URL
        else:
            base_url = settings.CDEK_API_URL

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{base_url}/orders/{order.track_number}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()

                status = data.get("state", None)
                if status is None:
                    raise CDEKError("CDEK order status not found in response")

                return await self.map_delivery_status(status)
            except (httpx.HTTPStatusError, KeyError) as e:
                raise CDEKError(f"Ошибка получения статуса заказа в СДЕК: {str(e)}")

    async def fill_schema(self, schema: OrderSchema) -> OrderSchema:
        try:
            delivery_info = await self.get_delivery_info(schema)
            tracking_info = await self.get_tracking_info(schema)
            delivery_point_info = await self.get_delivery_point_info(
                schema.delivery_point
            )

            # Обновляем схему
            schema.delivery_info = delivery_info
            schema.tracking_info = tracking_info
            schema.delivery_point_info = delivery_point_info

            return schema
        except CDEKError:
            # Если не удалось получить информацию, возвращаем схему как есть
            return schema

    async def get_delivery_info(self, order: OrderSchema) -> tp.Optional[DeliveryInfo]:
        if not order.track_number:
            return None

        try:
            # Получаем детальную информацию о пункте
            delivery_point = await self.get_delivery_point_info(order.delivery_point)

            # Получаем информацию о заказе из CDEK API
            order_data = await self._get_cdek_order_data(order.track_number)

            return DeliveryInfo(
                track_number=order.track_number,
                delivery_point_code=order.delivery_point,
                delivery_point_address=(
                    delivery_point.address if delivery_point else None
                ),
                delivery_point_name=delivery_point.name if delivery_point else None,
                delivery_point_working_hours=(
                    delivery_point.working_hours if delivery_point else None
                ),
                delivery_point_phone=delivery_point.phone if delivery_point else None,
                estimated_delivery_date=order_data.get("estimated_delivery_date"),
            )
        except CDEKError:
            return None

    async def get_tracking_info(self, order: OrderSchema) -> tp.Optional[TrackingInfo]:
        if not order.track_number:
            return None

        try:
            order_data = await self._get_cdek_order_data(order.track_number)

            # Формируем URL для отслеживания
            track_url = f"https://www.cdek.ru/track.html?order_id={order.track_number}"

            # Получаем читаемое описание статуса
            status = order_data.get("state", "")
            status_description = self._get_status_description(status)

            return TrackingInfo(
                track_number=order.track_number,
                track_url=track_url,
                delivery_service="CDEK",
                current_status=status,
                status_description=status_description,
                last_updated=order_data.get("date_updated"),
            )
        except CDEKError:
            return None

    async def get_delivery_point_info(
        self, delivery_point_code: str
    ) -> tp.Optional[DeliveryPoint]:
        try:
            token = await self.get_cdek_auth_token()

            if settings.CDEK_DEBUG:
                base_url = settings.CDEK_TEST_API_URL
            else:
                base_url = settings.CDEK_API_URL

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{base_url}/deliverypoints",
                    params={"code": delivery_point_code},
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()

                if not data or not isinstance(data, list) or len(data) == 0:
                    return None

                pvz = data[0]
                location = pvz.get("location", {})

                # Формируем координаты если есть
                coordinates = None
                if location.get("latitude") and location.get("longitude"):
                    coordinates = {
                        "latitude": location.get("latitude"),
                        "longitude": location.get("longitude"),
                    }

                # Формируем режим работы
                working_hours = None
                work_time = pvz.get("work_time")
                if work_time:
                    working_hours = self._format_working_hours(work_time)

                return DeliveryPoint(
                    code=delivery_point_code,
                    name=pvz.get("name", ""),
                    address=location.get("address_full", ""),
                    city=location.get("city", ""),
                    working_hours=working_hours,
                    phone=pvz.get("phone"),
                    coordinates=coordinates,
                    additional_info=pvz.get("note"),
                )
        except (httpx.HTTPStatusError, KeyError) as e:
            raise CDEKError(f"Ошибка получения информации о ПВЗ СДЕК: {str(e)}")

    async def _get_cdek_order_data(self, track_number: str) -> dict:
        """Получить данные заказа из CDEK API"""
        token = await self.get_cdek_auth_token()

        if settings.CDEK_DEBUG:
            base_url = settings.CDEK_TEST_API_URL
        else:
            base_url = settings.CDEK_API_URL

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/orders/{track_number}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()
            return response.json()

    def _get_status_description(self, status: str) -> str:
        """Получить человекочитаемое описание статуса"""
        descriptions = {
            "ACCEPTED": "Заказ принят",
            "CREATED": "Заказ создан",
            "RECEIVED_AT_SHIPMENT_WAREHOUSE": "Принят на склад отправителя",
            "READY_TO_SHIP_AT_SENDING_OFFICE": "Готов к отправке",
            "SENT_TO_RECIPIENT_CITY": "Отправлен в город получателя",
            "ACCEPTED_IN_RECIPIENT_CITY": "Прибыл в город получателя",
            "ACCEPTED_AT_PICK_UP_POINT": "Прибыл в пункт выдачи",
            "DELIVERED": "Доставлен",
            "NOT_DELIVERED": "Не доставлен",
            "TAKEN_BY_COURIER": "Передан курьеру",
            "POSTOMAT_POSTED": "Заложен в постамат",
            "POSTOMAT_RECEIVED": "Получен из постамата",
        }
        return descriptions.get(status, f"Статус: {status}")

    def _format_working_hours(self, work_time: list) -> tp.Optional[str]:
        """Форматировать режим работы"""
        if not work_time:
            return None

        formatted_hours = []
        for day_info in work_time:
            day = day_info.get("day")
            time_periods = day_info.get("periods", [])

            if not time_periods:
                continue

            day_names = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб", 7: "Вс"}

            day_name = day_names.get(day, str(day))
            time_str = ", ".join(
                [
                    f"{period.get('time_from', '')}-{period.get('time_to', '')}"
                    for period in time_periods
                ]
            )

            formatted_hours.append(f"{day_name}: {time_str}")

        return "; ".join(formatted_hours) if formatted_hours else None
