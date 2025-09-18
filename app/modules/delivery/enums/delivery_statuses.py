import enum


class DeliveryStatusesEnum(str, enum.Enum):
    CREATED = "CREATED"
    WAITING_FOR_PAYMENT = "WAITING_FOR_PAYMENT"
    PAID = "PAID"
    IN_PROGRESS = "IN_PROGRESS"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
