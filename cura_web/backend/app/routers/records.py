from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.idgen import PREFIXES, next_id
from app.models.medical_record import MedicalRecord
from app.models.surgery import Surgery
from app.schemas import MedicalRecordOut, SurgeryOut

router = APIRouter(prefix="/records", tags=["records"])

RECORD_PREFIX = PREFIXES["record"]
SURGERY_PREFIX = PREFIXES["surgery"]


@router.get("/medical", response_model=list[MedicalRecordOut])
async def list_medical(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MedicalRecord).order_by(MedicalRecord.recorded_at.desc()))
    return result.scalars().all()


@router.post("/medical", response_model=MedicalRecordOut, status_code=status.HTTP_201_CREATED)
async def create_medical(data: dict, db: AsyncSession = Depends(get_db)):
    if not data.get("record_number"):
        data["record_number"] = await next_id(db, MedicalRecord.record_number, RECORD_PREFIX)
    rec = MedicalRecord(**data)
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


@router.delete("/medical/{rec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical(rec_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == UUID(rec_id)))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404)
    await db.delete(r)
    await db.commit()


@router.get("/surgery", response_model=list[SurgeryOut])
async def list_surgeries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Surgery).order_by(Surgery.date.desc()))
    return result.scalars().all()


@router.post("/surgery", response_model=SurgeryOut, status_code=status.HTTP_201_CREATED)
async def create_surgery(data: dict, db: AsyncSession = Depends(get_db)):
    if not data.get("surgery_number"):
        data["surgery_number"] = await next_id(db, Surgery.surgery_number, SURGERY_PREFIX)
    s = Surgery(**data)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@router.delete("/surgery/{s_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_surgery(s_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(Surgery).where(Surgery.id == UUID(s_id)))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404)
    await db.delete(r)
    await db.commit()
