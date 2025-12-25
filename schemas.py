from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from enum import Enum


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
    amount: Annotated[Decimal, Field(gt=0, description="Сумма операции должна быть больше 0" )]

    model_config = ConfigDict(
        extra='forbid'
    )


class BalanceResponse(BaseModel):
    """Ответ с балансом (только для GET запроса)"""
    balance: Decimal
