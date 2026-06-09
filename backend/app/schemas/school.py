from pydantic import BaseModel


class SchoolSummary(BaseModel):
    id: int
    name: str
    city: str
    state: str
    ranking: int | None = None
