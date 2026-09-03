import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Payroll(Base):
    __tablename__ = "payrolls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_number: Mapped[str] = mapped_column(String(200), unique=True)
    doctor_name: Mapped[str | None] = mapped_column(String(200))
    doctor_number: Mapped[str | None] = mapped_column(String(200))
    doctor_email: Mapped[str | None] = mapped_column(String(200))
    salary: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
