import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_name: Mapped[str | None] = mapped_column(String(200))
    patient_age: Mapped[str | None] = mapped_column(String(200))
    patient_number: Mapped[str | None] = mapped_column(String(200))
    prescription_number: Mapped[str] = mapped_column(String(200), unique=True)
    patient_address: Mapped[str | None] = mapped_column(String(200))
    patient_type: Mapped[str | None] = mapped_column(String(200))
    ailment: Mapped[str | None] = mapped_column(String(200))
    instructions: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
