import os, uuid as _uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, Base
from app.core.idgen import PREFIXES, next_id
from app.models.patient import Patient, PatientType
from app.models.patient_transfer import PatientTransfer
from app.models.vitals import Vitals
from app.models.surgery import Surgery
from app.models.prescription import Prescription
from app.models.laboratory import LabRecord
from app.models.medical_record import MedicalRecord
from app.models.doctor import Doctor
from app.models.pharmaceutical import Pharmaceutical
from app.models.equipment import Equipment
from app.models.vendor import Vendor
from app.models.payroll import Payroll
from app.schemas import (
    PatientOut, PatientCreate, PatientTransferOut, DashboardStats,
    VitalsOut, SurgeryOut, PrescriptionOut, LabOut, MedicalRecordOut,
    DoctorOut,
)

router = APIRouter(prefix="/patients", tags=["patients"])

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

PATIENT_PREFIX = PREFIXES["patient"]


@router.get("/next-number")
async def next_patient_number(db: AsyncSession = Depends(get_db)):
    """Return the next available patient UID, e.g. 'C00A0001'."""
    number = await next_id(db, Patient.patient_number, PATIENT_PREFIX)
    return {"number": number}


# ─── CRUD ──────────────────────────────────────────────────────────────────────
@router.get("", response_model=list[PatientOut])
async def list_patients(
    search: str = Query(None, description="Search by patient number or name"),
    db: AsyncSession = Depends(get_db),
):
    q = select(Patient)
    if search:
        q = q.where(
            (Patient.patient_number.ilike(f"%{search}%"))
            | (Patient.first_name.ilike(f"%{search}%"))
            | (Patient.last_name.ilike(f"%{search}%"))
        )
    q = q.order_by(Patient.joined_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/search", response_model=list[PatientOut])
async def search_patients(q: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Patient)
        .where(
            (Patient.patient_number.ilike(f"%{q}%"))
            | (Patient.first_name.ilike(f"%{q}%"))
            | (Patient.last_name.ilike(f"%{q}%"))
        )
        .order_by(Patient.joined_at.desc())
        .limit(10)
    )
    return result.scalars().all()


@router.post("", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
async def create_patient(body: PatientCreate, db: AsyncSession = Depends(get_db)):
    patient_number = (body.patient_number or "").strip().upper() or None
    if not patient_number:
        patient_number = await next_id(db, Patient.patient_number, PATIENT_PREFIX)
    existing = await db.execute(select(Patient).where(Patient.patient_number == patient_number))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Patient number already exists")
    patient = Patient(
        first_name=body.first_name, last_name=body.last_name,
        date_of_birth=body.date_of_birth, age=body.age,
        patient_number=patient_number, address=body.address, phone=body.phone,
        ic_number=body.ic_number,
        patient_type=PatientType(body.patient_type), ailment=body.ailment,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p


@router.put("/{patient_id}", response_model=PatientOut)
async def update_patient(patient_id: str, body: PatientCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404, detail="Patient not found")
    for key in ["first_name", "last_name", "date_of_birth", "age", "address", "phone", "ic_number", "ailment"]:
        setattr(p, key, getattr(body, key, None))
    p.patient_type = PatientType(body.patient_type)
    await db.commit(); await db.refresh(p)
    return p


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404)
    await db.delete(p); await db.commit()


@router.put("/{patient_id}/discharge", response_model=PatientOut)
async def discharge_patient(patient_id: str, status_text: str = "Discharged", db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404)
    p.discharge_status = status_text
    await db.commit(); await db.refresh(p)
    return p


@router.put("/{patient_id}/readmit", response_model=PatientOut)
async def readmit_patient(patient_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404)
    p.discharge_status = None
    await db.commit(); await db.refresh(p)
    return p


# ─── Photo Upload ──────────────────────────────────────────────────────────────
@router.post("/{patient_id}/photo", response_model=PatientOut)
async def upload_photo(patient_id: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404)
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"patient_{patient_id}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    content = await file.read()
    with open(filepath, "wb") as f: f.write(content)
    p.photo = f"/uploads/{filename}"
    await db.commit(); await db.refresh(p)
    return p


# ─── Related Records ───────────────────────────────────────────────────────────
@router.get("/{patient_id}/vitals", response_model=list[VitalsOut])
async def patient_vitals(patient_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404)
    result = await db.execute(select(Vitals).where(Vitals.patient_number == p.patient_number).order_by(Vitals.recorded_at.desc()))
    return result.scalars().all()


@router.get("/{patient_id}/surgeries", response_model=list[SurgeryOut])
async def patient_surgeries(patient_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404)
    result = await db.execute(select(Surgery).where(Surgery.patient_number == p.patient_number).order_by(Surgery.date.desc()))
    return result.scalars().all()


@router.get("/{patient_id}/prescriptions", response_model=list[PrescriptionOut])
async def patient_prescriptions(patient_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404)
    result = await db.execute(select(Prescription).where(Prescription.patient_number == p.patient_number).order_by(Prescription.created_at.desc()))
    return result.scalars().all()


@router.get("/{patient_id}/lab-tests", response_model=list[LabOut])
async def patient_lab(patient_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404)
    result = await db.execute(select(LabRecord).where(LabRecord.patient_number == p.patient_number).order_by(LabRecord.recorded_at.desc()))
    return result.scalars().all()


@router.get("/{patient_id}/medical-records", response_model=list[MedicalRecordOut])
async def patient_med_records(patient_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.id == _uuid.UUID(patient_id)))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404)
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.patient_number == p.patient_number).order_by(MedicalRecord.recorded_at.desc()))
    return result.scalars().all()


# ─── Transfers ─────────────────────────────────────────────────────────────────
@router.get("/transfers/all", response_model=list[PatientTransferOut])
async def list_transfers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PatientTransfer))
    return result.scalars().all()


@router.post("/transfers", response_model=PatientTransferOut)
async def create_transfer(data: dict, db: AsyncSession = Depends(get_db)):
    transfer = PatientTransfer(**data)
    db.add(transfer)
    await db.commit(); await db.refresh(transfer)
    return transfer


# ─── Dashboard ─────────────────────────────────────────────────────────────────
@router.get("/stats/dashboard", response_model=DashboardStats)
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    async def count(model):
        r = await db.execute(select(func.count()).select_from(model))
        return r.scalar() or 0
    return DashboardStats(
        total_patients=await count(Patient),
        total_inpatients=await db.scalar(select(func.count()).select_from(Patient).where(Patient.patient_type == PatientType.INPATIENT)) or 0,
        total_outpatients=await db.scalar(select(func.count()).select_from(Patient).where(Patient.patient_type == PatientType.OUTPATIENT)) or 0,
        total_doctors=await count(Doctor),
        total_pharmaceuticals=await count(Pharmaceutical),
        total_equipment=await count(Equipment),
        total_vendors=await count(Vendor),
        total_payrolls=await count(Payroll),
    )