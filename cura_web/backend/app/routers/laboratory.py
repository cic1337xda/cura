from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.idgen import PREFIXES, next_id
from app.models.laboratory import LabRecord
from app.models.vitals import Vitals
from app.schemas import LabOut, VitalsOut

router = APIRouter(prefix="/lab", tags=["lab"])

LAB_PREFIX = PREFIXES["lab"]
VITALS_PREFIX = PREFIXES["vitals"]


@router.get("/tests", response_model=list[LabOut])
async def list_tests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LabRecord).order_by(LabRecord.recorded_at.desc()))
    return result.scalars().all()


@router.post("/tests", response_model=LabOut, status_code=status.HTTP_201_CREATED)
async def create_test(data: dict, db: AsyncSession = Depends(get_db)):
    if not data.get("lab_number"):
        data["lab_number"] = await next_id(db, LabRecord.lab_number, LAB_PREFIX)
    rec = LabRecord(**data)
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    return rec


@router.delete("/tests/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test(test_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(LabRecord).where(LabRecord.id == UUID(test_id)))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404)
    await db.delete(r)
    await db.commit()


@router.get("/vitals", response_model=list[VitalsOut])
async def list_vitals(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vitals).order_by(Vitals.recorded_at.desc()))
    return result.scalars().all()


@router.post("/vitals", response_model=VitalsOut, status_code=status.HTTP_201_CREATED)
async def create_vitals(data: dict, db: AsyncSession = Depends(get_db)):
    if not data.get("vitals_number"):
        data["vitals_number"] = await next_id(db, Vitals.vitals_number, VITALS_PREFIX)
    v = Vitals(**data)
    db.add(v)
    await db.commit()
    await db.refresh(v)
    return v


@router.delete("/vitals/{v_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vitals(v_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(Vitals).where(Vitals.id == UUID(v_id)))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404)
    await db.delete(r)
    await db.commit()
