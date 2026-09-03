from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr
import enum


# ─── Auth ──────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class DoctorLoginRequest(BaseModel):
    employee_number: str
    password: str


# ─── Admin ─────────────────────────────────────────────────────────────────────
class AdminOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    avatar: str | None

    class Config:
        from_attributes = True


# ─── Doctor ────────────────────────────────────────────────────────────────────
class DoctorCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    department: str | None = None
    ic_number: str | None = None
    employee_number: str | None = None


class DoctorOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    department: str | None
    ic_number: str | None = None
    employee_number: str
    avatar: str | None

    class Config:
        from_attributes = True


# ─── Patient ───────────────────────────────────────────────────────────────────
class PatientOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    date_of_birth: str | None
    age: str | None
    patient_number: str
    address: str | None
    phone: str | None
    ic_number: str | None = None
    patient_type: str
    ailment: str | None
    discharge_status: str | None
    photo: str | None
    joined_at: datetime

    class Config:
        from_attributes = True


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str | None = None
    age: str | None = None
    address: str | None = None
    phone: str | None = None
    ic_number: str | None = None
    patient_type: str = "OutPatient"
    ailment: str | None = None
    patient_number: str | None = None


class PatientTransferOut(BaseModel):
    id: UUID
    hospital: str | None
    date: str | None
    patient_name: str | None
    patient_number: str | None
    status: str | None

    class Config:
        from_attributes = True


# ─── Pharmacy ──────────────────────────────────────────────────────────────────
class CategoryOut(BaseModel):
    id: UUID
    name: str
    vendor: str | None
    description: str | None

    class Config:
        from_attributes = True


class PharmaceuticalOut(BaseModel):
    id: UUID
    name: str
    barcode: str | None
    description: str | None
    quantity: str | None
    category: str | None
    vendor: str | None

    class Config:
        from_attributes = True


class PrescriptionOut(BaseModel):
    id: UUID
    patient_name: str | None
    patient_age: str | None
    patient_number: str | None
    prescription_number: str
    patient_address: str | None
    patient_type: str | None
    ailment: str | None
    instructions: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Laboratory ────────────────────────────────────────────────────────────────
class LabOut(BaseModel):
    id: UUID
    patient_name: str | None
    ailment: str | None
    patient_number: str | None
    tests: str | None
    results: str | None
    lab_number: str
    recorded_at: datetime

    class Config:
        from_attributes = True


class VitalsOut(BaseModel):
    id: UUID
    vitals_number: str
    patient_number: str | None
    body_temp: str | None
    heart_pulse: str | None
    respiration_rate: str | None
    blood_pressure: str | None
    recorded_at: datetime

    class Config:
        from_attributes = True


# ─── Medical Records ───────────────────────────────────────────────────────────
class MedicalRecordOut(BaseModel):
    id: UUID
    record_number: str
    patient_name: str | None
    patient_address: str | None
    patient_age: str | None
    ailment: str | None
    patient_number: str | None
    prescription: str | None
    recorded_at: datetime

    class Config:
        from_attributes = True


# ─── Surgery ───────────────────────────────────────────────────────────────────
class SurgeryOut(BaseModel):
    id: UUID
    surgery_number: str
    doctor: str | None
    patient_number: str | None
    patient_name: str | None
    ailment: str | None
    date: datetime
    status: str | None

    class Config:
        from_attributes = True


# ─── Equipment ─────────────────────────────────────────────────────────────────
class EquipmentOut(BaseModel):
    id: UUID
    code: str | None
    name: str | None
    vendor: str | None
    description: str | None
    department: str | None
    status: str | None
    quantity: str | None

    class Config:
        from_attributes = True


# ─── Vendor ────────────────────────────────────────────────────────────────────
class VendorOut(BaseModel):
    id: UUID
    vendor_number: str
    name: str | None
    address: str | None
    mobile: str | None
    email: str | None
    phone: str | None
    description: str | None

    class Config:
        from_attributes = True


# ─── Account ───────────────────────────────────────────────────────────────────
class AccountOut(BaseModel):
    id: UUID
    name: str | None
    description: str | None
    account_type: str
    account_number: str
    amount: str | None

    class Config:
        from_attributes = True


# ─── Payroll ───────────────────────────────────────────────────────────────────
class PayrollOut(BaseModel):
    id: UUID
    payroll_number: str
    doctor_name: str | None
    doctor_number: str | None
    doctor_email: str | None
    salary: str | None
    status: str | None
    description: str | None
    generated_at: datetime

    class Config:
        from_attributes = True


# ─── Asset ─────────────────────────────────────────────────────────────────────
class AssetOut(BaseModel):
    id: UUID
    name: str | None
    description: str | None
    vendor: str | None
    status: str | None
    department: str | None

    class Config:
        from_attributes = True


# ─── Dashboard ─────────────────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_patients: int
    total_inpatients: int
    total_outpatients: int
    total_doctors: int
    total_pharmaceuticals: int
    total_equipment: int
    total_vendors: int
    total_payrolls: int
