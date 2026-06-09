from fastapi import APIRouter

from app.schemas.match import MatchRequest, MatchResponse

router = APIRouter()


@router.post("/preview", response_model=MatchResponse)
def preview_match(payload: MatchRequest) -> MatchResponse:
    # Architecture-only placeholder implementation.
    # Real matching logic and persistence are intentionally out of scope for this scaffold.
    score = round((payload.gpa / 4.0) * 50 + (payload.lsat_score / 180.0) * 50, 2)
    return MatchResponse(recommended_school_ids=[1], confidence_score=score)
