import uuid
import datetime
from decimal import Decimal

from sqlalchemy import UUID, DateTime, func, Numeric, ForeignKey
from enum import Enum as PyEnum
from sqlalchemy import Enum as SA_Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Wallet(Base):
    """
    Модель таблицы кошелька
    """
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    balance: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal('0.00'),
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="wallet",
        lazy="selectin"
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )


class OperationType(str, PyEnum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class TransactionStatus(str, PyEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Transaction(Base):
    """
    Модель таблицы Транзакции
    """
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("wallets.id", ondelete="CASCADE"),
        nullable=False
    )

    wallet: Mapped[Wallet] = relationship(
        "Wallet",
        back_populates="transactions",
        lazy="selectin"
    )

    operation_type: Mapped[OperationType] = mapped_column(
        SA_Enum(OperationType),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False
    )

    status: Mapped[TransactionStatus] = mapped_column(
        SA_Enum(TransactionStatus),
        default=TransactionStatus.PENDING,
        nullable=False
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )
