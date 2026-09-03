from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func, text
from sqlalchemy.exc import ProgrammingError
from app.core.database import engine, Base, async_session
from app.core.security import hash_password
from app.models.admin import Admin
from app.routers import auth, patients, doctors, pharmacy, laboratory, records, operations

# Import all models to register them with Base
import app.models  # noqa: F401


async def seed_default_admin():
    async with async_session() as db:
        result = await db.execute(select(func.count()).select_from(Admin))
        count = result.scalar()
        if count == 0:
            admin = Admin(
                first_name="System",
                last_name="Administrator",
                email="admin@mail.com",
                password=hash_password("Password@123"),
            )
            db.add(admin)
            await db.commit()


async def run_migrations():
    async with engine.begin() as conn:
        for col_sql in [
            "ALTER TABLE patients ADD COLUMN IF NOT EXISTS photo VARCHAR(500)",
            "ALTER TABLE patients ADD COLUMN IF NOT EXISTS ic_number VARCHAR(50)",
            "ALTER TABLE doctors ADD COLUMN IF NOT EXISTS ic_number VARCHAR(50)",
        ]:
            try:
                await conn.execute(text(col_sql))
            except Exception:
                try:
                    # PostgreSQL < 9.6 doesn't support IF NOT EXISTS for ADD COLUMN
                    await conn.execute(text(col_sql.replace(" IF NOT EXISTS", "")))
                except Exception:
                    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await run_migrations()
    await seed_default_admin()
    yield
    await engine.dispose()


app = FastAPI(
    title="Cura. HMS API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(pharmacy.router)
app.include_router(laboratory.router)
app.include_router(records.router)
app.include_router(operations.router)


@app.get("/")
async def root():
    return {"service": "Cura. HMS API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
