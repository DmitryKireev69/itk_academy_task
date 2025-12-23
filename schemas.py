from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum
import uuid
from datetime import datetime


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class OperationRequest(BaseModel):
    """
    Запрос на операцию с кошельком
    """
    operation_type: OperationType
    amount: Decimal = Field(
        gt=0,
        le=1000000000,
        description="Сумма операции (должна быть > 0)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "operation_type": "DEPOSIT",
                "amount": 1000.00
            }
        }


class TransactionResponse(BaseModel):
    """
    Ответ с информацией о транзакции
    """
    id: uuid.UUID
    wallet_id: uuid.UUID
    operation_type: OperationType
    amount: Decimal
    status: TransactionStatus
    created_at: datetime

    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    """Ответ с балансом (только для GET запроса)"""
    balance: Decimal
