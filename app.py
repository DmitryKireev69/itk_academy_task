import uuid
import logging

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_session
from schemas import OperationRequest, BalanceResponse
from crud import get_wallet_balance, InsufficientFundsError, perform_wallet_operation


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Wallet API",
    description="REST API для управления кошельками пользователей",
    version="1.0.0"
)


@app.get(
    "/api/v1/wallets/{wallet_id}",
    response_model=BalanceResponse,
    summary="Получить баланс кошелька",
    description="Возвращает текущий баланс кошелька. Если кошелёк не существует, возвращает баланс 0.",
    responses={
        400: {"description": "Неверный формат UUID"},
        200: {"description": "Успешный запрос"}
    }
)
async def get_wallet_balance_endpoint(
        wallet_id: str,
        db: AsyncSession = Depends(get_db_session)
):
    """
    Получить баланс кошелька по UUID.

    - Если кошелёк существует: возвращает текущий баланс
    - Если кошелёк не существует: возвращает баланс 0
    """
    try:
        wallet_uuid = uuid.UUID(wallet_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат UUID"
        )

    try:
        balance = await get_wallet_balance(db, wallet_uuid)
        return BalanceResponse(balance=balance)
    except Exception as e:
        logger.error(f"Error getting wallet balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post(
    "/api/v1/wallets/{wallet_id}/operation",
    response_model=BalanceResponse,
    summary="Изменить баланс кошелька"
)
async def wallet_operation_endpoint(
        wallet_id: str,
        operation: OperationRequest,
        db: AsyncSession = Depends(get_db_session)
):
    """
    Выполнить операцию с кошельком.

    - DEPOSIT: пополнение если кошелька нет создаст его и добавит указанную сумму
    - WITHDRAW: снятие (проверяет достаточно ли денег)
    """
    try:
        wallet_uuid = uuid.UUID(wallet_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат UUID"
        )

    try:
        wallet, _ = await perform_wallet_operation(db, wallet_uuid, operation)

        return BalanceResponse(balance=wallet.balance)

    except InsufficientFundsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(500, "Внутренняя ошибка сервера")


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db_session)):
    """Проверка подключения к бд"""
    try:
        # Простая проверка подключения к БД
        await db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Wallet API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "get_balance": "GET /api/v1/wallets/{wallet_id}",
            "perform_operation": "POST /api/v1/wallets/{wallet_id}/operation",
            "health_check": "GET /health"
        }
    }
