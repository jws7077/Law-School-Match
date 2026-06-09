const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function apiPath(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export type MatchRequest = {
  gpa: number;
  lsat_score: number;
  preferred_states: string[];
  career_goals: string[];
  cost_sensitivity: number;
};

export type RankedSchool = {
  school_id: number;
  name: string;
  city: string;
  state: string;
  match_score: number;
  admissions_fit: number;
  geographic_fit: number;
  career_fit: number;
  cost_fit: number;
  classification: string;
  explanation: string;
  matched_career_goals: string[];
};

export type MatchResponse = {
  ranked_schools: RankedSchool[];
};

export async function requestSchoolMatches(payload: MatchRequest): Promise<MatchResponse> {
  const response = await fetch(apiPath("/api/v1/matches/rank"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Match request failed with status ${response.status}`);
  }

  return response.json() as Promise<MatchResponse>;
}
