import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import enum


class PatientType(str, enum.Enum):
    INPATIENT = "InPatient"
    OUTPATIENT = "OutPatient"


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(200))
    last_name: Mapped[str] = mapped_column(String(200))
    date_of_birth: Mapped[str | None] = mapped_column(String(200))
    age: Mapped[str | None] = mapped_column(String(200))
    patient_number: Mapped[str] = mapped_column(String(200), unique=True)
    address: Mapped[str | None] = mapped_column(String(200))
    ic_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(200))
    patient_type: Mapped[PatientType] = mapped_column(SAEnum(PatientType))
    ailment: Mapped[str | None] = mapped_column(String(200))
    discharge_status: Mapped[str | None] = mapped_column(String(200), nullable=True)
    photo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
