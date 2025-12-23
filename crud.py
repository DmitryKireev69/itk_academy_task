# crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
import uuid

from models import Wallet, Transaction, OperationType, TransactionStatus
from schemas import OperationRequest


class InsufficientFundsError(Exception):
    """Недостаточно средств на кошельке"""
    pass


async def get_wallet_balance(
        db: AsyncSession,
        wallet_id: uuid.UUID
) -> Decimal:
    """
    Получить баланс кошелька.
    Если кошелёк не существует - возвращает 0.
    """
    result = await db.execute(
        select(Wallet.balance).where(Wallet.id == wallet_id)
    )

    balance = result.scalar_one_or_none()

    return balance if balance is not None else Decimal('0')


async def perform_wallet_operation(
        db: AsyncSession,
        wallet_id: uuid.UUID,
        operation: OperationRequest
):
    """
    Выполнить операцию с кошельком (депозит/снятие)
    """
    async with db.begin():
        result = await db.execute(
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .with_for_update()
        )
        wallet = result.scalar_one_or_none()

        if not wallet:
            wallet = Wallet(id=wallet_id, balance=Decimal('0'))
            db.add(wallet)
            await db.flush()

        transaction = Transaction(
            wallet_id=wallet_id,
            operation_type=operation.operation_type,
            amount=operation.amount,
            status=TransactionStatus.PENDING  # Сначала "в процессе"
        )
        db.add(transaction)
        await db.flush()

        if operation.operation_type == OperationType.WITHDRAW:
            if wallet.balance < operation.amount:
                transaction.status = TransactionStatus.FAILED
                await db.flush()
                raise InsufficientFundsError(
                    f"Недостаточно средств. Доступно: {wallet.balance}"
                )

        if operation.operation_type == OperationType.DEPOSIT:
            wallet.balance += operation.amount
        else:
            wallet.balance -= operation.amount

        transaction.status = TransactionStatus.COMPLETED

        return wallet, transaction
