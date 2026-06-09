from fastapi import APIRouter, HTTPException

from app.data.mock_schools import MOCK_SCHOOLS
from app.schemas.school import SchoolSummary

router = APIRouter()

SCHOOLS = [
    SchoolSummary(id=school.school_id, name=school.name, city=school.city, state=school.state, ranking=index + 1)
    for index, school in enumerate(MOCK_SCHOOLS)
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
