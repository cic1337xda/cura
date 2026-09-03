from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.idgen import PREFIXES, next_id
from app.models.pharmaceutical_category import PharmaceuticalCategory
from app.models.pharmaceutical import Pharmaceutical
from app.models.prescription import Prescription
from app.schemas import CategoryOut, PharmaceuticalOut, PrescriptionOut

router = APIRouter(prefix="/pharmacy", tags=["pharmacy"])

RX_PREFIX = PREFIXES["prescription"]


# ─── Categories ────────────────────────────────────────────────────────────────
@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PharmaceuticalCategory))
    return result.scalars().all()


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(data: dict, db: AsyncSession = Depends(get_db)):
    cat = PharmaceuticalCategory(**data)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.delete("/categories/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(cat_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(PharmaceuticalCategory).where(PharmaceuticalCategory.id == UUID(cat_id)))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(c)
    await db.commit()


# ─── Pharmaceuticals ───────────────────────────────────────────────────────────
@router.get("/drugs", response_model=list[PharmaceuticalOut])
async def list_drugs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pharmaceutical))
    return result.scalars().all()


@router.post("/drugs", response_model=PharmaceuticalOut, status_code=status.HTTP_201_CREATED)
async def create_drug(data: dict, db: AsyncSession = Depends(get_db)):
    drug = Pharmaceutical(**data)
    db.add(drug)
    await db.commit()
    await db.refresh(drug)
    return drug


@router.delete("/drugs/{drug_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_drug(drug_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(Pharmaceutical).where(Pharmaceutical.id == UUID(drug_id)))
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Drug not found")
    await db.delete(d)
    await db.commit()


# ─── Prescriptions ─────────────────────────────────────────────────────────────
@router.get("/prescriptions", response_model=list[PrescriptionOut])
async def list_prescriptions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Prescription).order_by(Prescription.created_at.desc()))
    return result.scalars().all()


@router.post("/prescriptions", response_model=PrescriptionOut, status_code=status.HTTP_201_CREATED)
async def create_prescription(data: dict, db: AsyncSession = Depends(get_db)):
    if not data.get("prescription_number"):
        data["prescription_number"] = await next_id(db, Prescription.prescription_number, RX_PREFIX)
    rx = Prescription(**data)
    db.add(rx)
    await db.commit()
    await db.refresh(rx)
    return rx


@router.delete("/prescriptions/{rx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prescription(rx_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(Prescription).where(Prescription.id == UUID(rx_id)))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Prescription not found")
    await db.delete(r)
    await db.commit()
