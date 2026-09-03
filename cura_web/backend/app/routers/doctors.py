import os, uuid as _uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.idgen import PREFIXES, next_id
from app.core.security import hash_password
from app.models.doctor import Doctor
from app.schemas import DoctorCreate, DoctorOut

router = APIRouter(prefix="/doctors", tags=["doctors"])
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

DOCTOR_PREFIX = PREFIXES["doctor"]


@router.get("/next-number")
async def next_doctor_number(db: AsyncSession = Depends(get_db)):
    """Return the next available doctor employee UID, e.g. 'C01A0001'."""
    number = await next_id(db, Doctor.employee_number, DOCTOR_PREFIX)
    return {"number": number}


@router.get("", response_model=list[DoctorOut])
async def list_doctors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Doctor))
    return result.scalars().all()


@router.post("", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
async def create_doctor(body: DoctorCreate, db: AsyncSession = Depends(get_db)):
    employee_number = (body.employee_number or "").strip().upper() or None
    if not employee_number:
        employee_number = await next_id(db, Doctor.employee_number, DOCTOR_PREFIX)
    existing = await db.execute(select(Doctor).where(Doctor.employee_number == employee_number))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Employee number already exists")
    doc = Doctor(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        password=hash_password(body.password),
        department=body.department,
        ic_number=body.ic_number,
        employee_number=employee_number,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get("/{doctor_id}", response_model=DoctorOut)
async def get_doctor(doctor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Doctor).where(Doctor.id == _uuid.UUID(doctor_id)))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return d


@router.put("/{doctor_id}", response_model=DoctorOut)
async def update_doctor(doctor_id: str, body: DoctorCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Doctor).where(Doctor.id == _uuid.UUID(doctor_id)))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    d.first_name = body.first_name
    d.last_name = body.last_name
    d.email = body.email
    d.department = body.department
    d.ic_number = body.ic_number
    if body.employee_number:
        d.employee_number = body.employee_number
    if body.password:
        d.password = hash_password(body.password)
    await db.commit()
    await db.refresh(d)
    return d


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(doctor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Doctor).where(Doctor.id == _uuid.UUID(doctor_id)))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    await db.delete(d)
    await db.commit()


@router.post("/{doctor_id}/photo", response_model=DoctorOut)
async def upload_doctor_photo(doctor_id: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Doctor).where(Doctor.id == _uuid.UUID(doctor_id)))
    d = result.scalar_one_or_none()
    if not d: raise HTTPException(status_code=404)
    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"doctor_{doctor_id}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    content = await file.read()
    with open(filepath, "wb") as f: f.write(content)
    d.avatar = f"/uploads/{filename}"
    await db.commit(); await db.refresh(d)
    return d
