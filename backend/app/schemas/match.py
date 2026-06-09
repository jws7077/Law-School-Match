from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    gpa: float = Field(ge=0.0, le=4.0)
    lsat_score: int = Field(ge=120, le=180)
    preferred_states: list[str] = Field(default_factory=list)
    career_goals: list[str] = Field(default_factory=list)
    career_path_weights: dict[str, int] = Field(default_factory=dict)
    cost_sensitivity: int = Field(ge=1, le=10)


class RankedSchool(BaseModel):
    school_id: int
    name: str
    city: str
    state: str
    match_score: float = Field(ge=0, le=100)
    admissions_fit: float = Field(ge=0, le=100)
    geographic_fit: float = Field(ge=0, le=100)
    career_fit: float = Field(ge=0, le=100)
    career_outcome_fit: float = Field(ge=0, le=100)
    cost_fit: float = Field(ge=0, le=100)
    classification: str
    explanation: str
    matched_career_goals: list[str] = Field(default_factory=list)


class MatchResponse(BaseModel):
    ranked_schools: list[RankedSchool]
