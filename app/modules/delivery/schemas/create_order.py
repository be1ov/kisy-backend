import typing as tp

from pydantic import BaseModel


class CdekPackageItem(BaseModel):
    ware_key: str
    name: str
    cost: float
    weight: int
    amount: int
    payment: dict

class CdekPackage(BaseModel):
    number: str
    weight: int
    length: int
    width: int
    height: int
    items: tp.List[CdekPackageItem]

class CdekRecipient(BaseModel):
    name: str
    phones: tp.List[dict]