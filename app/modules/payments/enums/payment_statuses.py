from enum import Enum


class PaymentStatuses(str, Enum):
    CREATED = 'CREATED'
    SUCCESS = 'SUCCESS'