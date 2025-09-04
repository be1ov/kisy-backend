from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_session
from app.modules.orders.entities import OrderEntity
from app.modules.payments.entities import PaymentEntity
from app.modules.payments.enums.payment_methods import PaymentMethods
from app.modules.payments.enums.payment_statuses import PaymentStatuses
from app.modules.payments.service import PaymentService
from app.modules.delivery.methods.cdek import CDEKDeliveryMethod
from app.modules.users.entities import UserEntity


class PaymentIntegrationService:
    def __init__(self, payments_service: PaymentService = Depends(), db: AsyncSession = Depends(get_session), cdek_service: CDEKDeliveryMethod = Depends()):
        self.payments_service = payments_service
        self.cdek_service = cdek_service
        self.db = db

    async def process_payment(self, method: str, body):
        payment_method_service = self.payments_service.get_payment_method(PaymentMethods(method))
        print('jopa')
        payment_id = await payment_method_service.process_payment(body)
        print('konec jopi')

        stmt = select(PaymentEntity).where(PaymentEntity.id == payment_id)
        result = await self.db.execute(stmt)
        payment = result.scalars().first()
        if payment is None:
            print(f"Payment not found with id: {payment_id}")
            raise ValueError(f"Payment not found with id: {payment_id}")

        payment.status = PaymentStatuses.SUCCESS

        self.db.add(payment)
        await self.db.commit()

        order: OrderEntity = payment.order

        current_user: UserEntity = order.user

        await self.cdek_service.prepare_cdek_data(order, order.id, current_user)
