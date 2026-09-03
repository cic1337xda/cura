import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Vitals(Base):
    __tablename__ = "vitals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vitals_number: Mapped[str] = mapped_column(String(200), unique=True)
    patient_number: Mapped[str | None] = mapped_column(String(200))
    body_temp: Mapped[str | None] = mapped_column(String(200))
    heart_pulse: Mapped[str | None] = mapped_column(String(200))
    respiration_rate: Mapped[str | None] = mapped_column(String(200))
    blood_pressure: Mapped[str | None] = mapped_column(String(200))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
