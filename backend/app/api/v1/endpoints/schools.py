from fastapi import APIRouter, HTTPException

from app.schemas.school import SchoolSummary

router = APIRouter()

# Placeholder in-memory dataset for architecture scaffolding only.
SCHOOLS = [
    SchoolSummary(id=1, name="Example Law School", city="New York", state="NY", ranking=42)
]


@router.get("", response_model=list[SchoolSummary])
def list_schools() -> list[SchoolSummary]:
    return SCHOOLS


@router.get("/{school_id}", response_model=SchoolSummary)
def get_school(school_id: int) -> SchoolSummary:
    for school in SCHOOLS:
        if school.id == school_id:
            return school
    raise HTTPException(status_code=404, detail="School not found")
