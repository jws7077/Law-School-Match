from pydantic import BaseModel, Field


class StudentProfileCreate(BaseModel):
    email: str
    gpa: float = Field(ge=0.0, le=4.0)
    lsat_score: int = Field(ge=120, le=180)
    geographic_preferences: list[str] = Field(default_factory=list)
    career_goals: list[str] = Field(default_factory=list)
    cost_sensitivity: int = Field(ge=1, le=5)
    lifestyle_preferences: list[str] = Field(default_factory=list)
