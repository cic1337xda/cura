import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class PatientTransfer(Base):
    __tablename__ = "patient_transfers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital: Mapped[str | None] = mapped_column(String(200))
    date: Mapped[str | None] = mapped_column(String(200))
    patient_name: Mapped[str | None] = mapped_column(String(200))
    patient_number: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str | None] = mapped_column(String(200))
