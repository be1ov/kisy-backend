import typing as tp
import uuid

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_session
from app.core.dependencies.get_current_user import get_current_user
from app.modules.orders.service import OrderService, UndefinedOrder
from app.modules.payments.entities import PaymentMethodEntity, PaymentEntity
from app.modules.payments.enums.payment_methods import PaymentMethods
from app.modules.payments.enums.payment_statuses import PaymentStatuses
from app.modules.payments.methods.base import BasePaymentMethod
from app.modules.payments.methods.yookassa import YookassaPaymentMethod
from app.modules.payments.schemas.generate_payment_link import GeneratePaymentLinkSchema
from app.modules.users.entities import UserEntity


class PaymentLinkGenerationError(ValueError):
    pass


class PaymentService:
    def __init__(self, orders_service: OrderService = Depends(), db: AsyncSession = Depends(get_session)):
        self._orders_service = orders_service
        self._db = db

    @staticmethod
    def get_payment_methods() -> tp.List[PaymentMethodEntity]:
        """
        Returns all payment methods

        :return:
        """
        return [
            PaymentMethodEntity(name="ЮКасса", code=PaymentMethods.YOOKASSA)
        ]

    @staticmethod
    def _get_payment_methods() -> tp.Dict[PaymentMethods, tp.Type[BasePaymentMethod]]:
        return {
            PaymentMethods.YOOKASSA: YookassaPaymentMethod
        }

    @staticmethod
    def _get_payment_method(method: PaymentMethods) -> BasePaymentMethod:
        return PaymentService._get_payment_methods()[method]()

    async def generate_payment_link(self, data: GeneratePaymentLinkSchema,
                                    current_user: UserEntity = Depends(get_current_user)) -> str:
        """
        Generates payment link for order

        :param data:
        :param current_user:
        :return:
        """
        method = self._get_payment_method(data.method)

        try:
            order = await self._orders_service.get_by_id(data.order_id)
        except UndefinedOrder:
            raise PaymentLinkGenerationError("Undefined order")

        if order.user != current_user:
            raise PaymentLinkGenerationError("Only owner of the order can generate payment link")

        if any(payment.status == PaymentStatuses.SUCCESS for payment in order.payments):
            raise PaymentLinkGenerationError("Payment is already paid")

        payment_id = str(uuid.uuid4())

        try:
            link = await method.get_payment_link(order, payment_id)
        except:
            raise PaymentLinkGenerationError("There was an error generating payment link")

        try:
            async with self._db.begin():
                payment = PaymentEntity(
                    id=payment_id,
                    method=data.method,
                    order=order,
                    link=link
                )
                self._db.add(payment)
        except Exception as e:
            raise PaymentLinkGenerationError("There was an error while saving payment link")
