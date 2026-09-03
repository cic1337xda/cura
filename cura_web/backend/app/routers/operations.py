from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.idgen import PREFIXES, next_id
from app.models.equipment import Equipment
from app.models.vendor import Vendor
from app.models.account import Account
from app.models.payroll import Payroll
from app.models.asset import Asset
from app.schemas import EquipmentOut, VendorOut, AccountOut, PayrollOut, AssetOut

router = APIRouter(prefix="/ops", tags=["ops"])

VENDOR_PREFIX = PREFIXES["vendor"]
ACCOUNT_PREFIX = PREFIXES["account"]
PAYROLL_PREFIX = PREFIXES["payroll"]


# ─── Equipment ─────────────────────────────────────────────────────────────────
@router.get("/equipment", response_model=list[EquipmentOut])
async def list_equipment(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Equipment))
    return result.scalars().all()


@router.post("/equipment", response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
async def create_equipment(data: dict, db: AsyncSession = Depends(get_db)):
    eq = Equipment(**data)
    db.add(eq)
    await db.commit()
    await db.refresh(eq)
    return eq


@router.delete("/equipment/{eq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(eq_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(Equipment).where(Equipment.id == UUID(eq_id)))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404)
    await db.delete(r)
    await db.commit()


# ─── Vendors ───────────────────────────────────────────────────────────────────
@router.get("/vendors", response_model=list[VendorOut])
async def list_vendors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vendor))
    return result.scalars().all()


@router.post("/vendors", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
async def create_vendor(data: dict, db: AsyncSession = Depends(get_db)):
    if not data.get("vendor_number"):
        data["vendor_number"] = await next_id(db, Vendor.vendor_number, VENDOR_PREFIX)
    v = Vendor(**data)
    db.add(v)
    await db.commit()
    await db.refresh(v)
    return v


@router.delete("/vendors/{v_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(v_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(Vendor).where(Vendor.id == UUID(v_id)))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404)
    await db.delete(r)
    await db.commit()


# ─── Accounts ─────────────────────────────────────────────────────────────────
@router.get("/accounts", response_model=list[AccountOut])
async def list_accounts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account))
    return result.scalars().all()


@router.post("/accounts", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
async def create_account(data: dict, db: AsyncSession = Depends(get_db)):
    if not data.get("account_number"):
        data["account_number"] = await next_id(db, Account.account_number, ACCOUNT_PREFIX)
    a = Account(**data)
    db.add(a)
    await db.commit()
    await db.refresh(a)
    return a


@router.delete("/accounts/{acc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(acc_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(Account).where(Account.id == UUID(acc_id)))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404)
    await db.delete(r)
    await db.commit()


# ─── Payroll ──────────────────────────────────────────────────────────────────
@router.get("/payrolls", response_model=list[PayrollOut])
async def list_payrolls(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payroll).order_by(Payroll.generated_at.desc()))
    return result.scalars().all()


@router.post("/payrolls", response_model=PayrollOut, status_code=status.HTTP_201_CREATED)
async def create_payroll(data: dict, db: AsyncSession = Depends(get_db)):
    if not data.get("payroll_number"):
        data["payroll_number"] = await next_id(db, Payroll.payroll_number, PAYROLL_PREFIX)
    p = Payroll(**data)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.delete("/payrolls/{pay_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payroll(pay_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    result = await db.execute(select(Payroll).where(Payroll.id == UUID(pay_id)))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404)
    await db.delete(r)
    await db.commit()


# ─── Assets ────────────────────────────────────────────────────────────────────
@router.get("/assets", response_model=list[AssetOut])
async def list_assets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset))
    return result.scalars().all()


@router.post("/assets", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
async def create_asset(data: dict, db: AsyncSession = Depends(get_db)):
    a = Asset(**data)
    db.add(a)
    await db.commit()
    await db.refresh(a)
    return a
