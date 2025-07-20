import typing as tp

from pydantic import BaseModel


class CdekPackageItem(BaseModel):
    ware_key: str
    name: str
    cost: float
    weight: float
    amount: float
    payment: dict

class CdekPackage(BaseModel):
    number: str
    weight: float
    length: float
    width: float
    height: float
    items: tp.List[CdekPackageItem]

class CdekRecipient(BaseModel):
    name: str
    phones: tp.List[dict]