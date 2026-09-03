from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.admin import Admin
from app.models.doctor import Doctor
from app.schemas import LoginRequest, DoctorLoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).where(Admin.email == body.email))
    admin = result.scalar_one_or_none()
    if not admin or not verify_password(body.password, admin.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(admin.id), "role": "admin"})
    return TokenResponse(access_token=token, role="admin")


@router.post("/doctor/login", response_model=TokenResponse)
async def doctor_login(body: DoctorLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Doctor).where(Doctor.employee_number == body.employee_number))
    doc = result.scalar_one_or_none()
    if not doc or not verify_password(body.password, doc.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(doc.id), "role": "doctor", "doc_number": doc.employee_number})
    return TokenResponse(access_token=token, role="doctor")
