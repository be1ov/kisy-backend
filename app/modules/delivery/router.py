from fastapi import APIRouter, Depends

from app.modules.delivery.schemas.get_cities import CityFilter, DeliveryPointFilter
from app.modules.delivery.schemas.get_countries import GetCountriesSchema
from app.modules.delivery.service import DeliveryService

router = APIRouter()


@router.get("/methods")
async def get_delivery_methods(service: DeliveryService = Depends()):
    return service.get_all_methods()


@router.get("/countries")
async def get_countries(
    body: GetCountriesSchema = Depends(), service: DeliveryService = Depends()
):
    return await service.get_countries(body)


@router.get("/cities")
async def get_cities(
    body: CityFilter = Depends(), service: DeliveryService = Depends()
):
    return await service.get_cities(body)


@router.get("/delivery")
async def get_delivery(
    body: DeliveryPointFilter = Depends(), service: DeliveryService = Depends()
):
    return await service.get_addresses(body)
