"""Sequential, prefix-based ID generation for Cura. HMS.

The NFC card UID format is:  <PREFIX><4-digit number>   (e.g. "C00A0001").
The prefix is a hard-coded 4-character HEX header "C##A" and the tail is a
zero-padded patient/entity number (1 - 9999).

Backend is the single source of truth for the "next available number" so that
race conditions from the browser are avoided.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Entity → 4-char HEX prefix (NFC header)
PREFIXES = {
    "patient": "C00A",
    "doctor": "C01A",
    "prescription": "C02A",
    "lab": "C03A",
    "vitals": "C04A",
    "record": "C05A",
    "surgery": "C06A",
    "vendor": "C07A",
    "account": "C08A",
    "payroll": "C09A",
}


def make_number(prefix: str, n: int) -> str:
    """Return the full 8-char ID, e.g. C00A0001."""
    return f"{prefix}{n:04d}"


def parse_number(value: str, prefix: str) -> int | None:
    """Extract the numeric tail from a stored ID if it matches prefix."""
    if not value or not value.startswith(prefix):
        return None
    tail = value[len(prefix):]
    if not tail.isdigit():
        return None
    return int(tail)


async def next_number(db: AsyncSession, column, prefix: str) -> int:
    """Find the max numeric tail across existing rows and return max + 1."""
    result = await db.execute(select(column))
    max_n = 0
    for (val,) in result.all():
        n = parse_number(val, prefix)
        if n is not None and n > max_n:
            max_n = n
    return max_n + 1


async def next_id(db: AsyncSession, column, prefix: str) -> str:
    """Return the next available full ID for a given column + prefix."""
    return make_number(prefix, await next_number(db, column, prefix))