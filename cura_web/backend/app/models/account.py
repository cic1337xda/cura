import uuid
from sqlalchemy import String, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class AccountType(str, enum.Enum):
    PAYABLE = "Payable Account"
    RECEIVABLE = "Receivable Account"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    account_type: Mapped[AccountType] = mapped_column(SAEnum(AccountType))
    account_number: Mapped[str] = mapped_column(String(200), unique=True)
    amount: Mapped[str | None] = mapped_column(String(200))
