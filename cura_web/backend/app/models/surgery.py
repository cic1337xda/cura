import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Surgery(Base):
    __tablename__ = "surgeries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    surgery_number: Mapped[str] = mapped_column(String(200), unique=True)
    doctor: Mapped[str | None] = mapped_column(String(200))
    patient_number: Mapped[str | None] = mapped_column(String(200))
    patient_name: Mapped[str | None] = mapped_column(String(200))
    ailment: Mapped[str | None] = mapped_column(String(200))
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    status: Mapped[str | None] = mapped_column(String(200))
