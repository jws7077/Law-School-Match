from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MockSchool:
    school_id: int
    name: str
    city: str
    state: str
    median_gpa: float
    median_lsat: int
    tuition_tier: int
    career_strengths: dict[str, int]


CAREER_PATHS = (
    ("biglaw", "BigLaw"),
    ("government", "Government"),
    ("public-interest", "Public Interest"),
    ("judicial-clerkship", "Judicial Clerkships"),
    ("prosecutor", "Prosecutor Careers"),
    ("litigation", "Litigation"),
    ("judicial-career", "Judicial Careers"),
    ("public-defender", "Public Defender"),
    ("judge", "Judge"),
)

CAREER_ALIASES = {
    "big law": "biglaw",
    "biglaw": "biglaw",
    "corporate law": "biglaw",
    "government": "government",
    "public interest": "public-interest",
    "public-interest": "public-interest",
    "public defender": "public-defender",
    "public defenders": "public-defender",
    "judicial clerkship": "judicial-clerkship",
    "judicial clerkships": "judicial-clerkship",
    "clerkship": "judicial-clerkship",
    "clerkships": "judicial-clerkship",
    "judge": "judge",
    "judicial": "judge",
    "prosecutor": "prosecutor",
    "prosecutor careers": "prosecutor",
    "litigation": "litigation",
    "judicial career": "judicial-career",
    "judicial careers": "judicial-career",
}

MOCK_SCHOOLS: tuple[MockSchool, ...] = (
    MockSchool(1, "Yale Law School", "New Haven", "CT", 3.96, 174, 5, {"judicial-career": 5, "judicial-clerkship": 5, "public-interest": 4, "judge": 5, "public-defender": 3}),
    MockSchool(2, "Stanford Law School", "Stanford", "CA", 3.92, 173, 5, {"biglaw": 5, "judicial-career": 4, "government": 3, "judge": 4, "litigation": 4}),
    MockSchool(3, "Harvard Law School", "Cambridge", "MA", 3.93, 174, 5, {"biglaw": 5, "government": 4, "judicial-clerkship": 4, "judge": 5, "public-interest": 4}),
    MockSchool(4, "University of Chicago Law School", "Chicago", "IL", 3.91, 173, 5, {"biglaw": 5, "judicial-clerkship": 5, "government": 4, "judge": 5, "litigation": 4}),
    MockSchool(5, "Columbia Law School", "New York", "NY", 3.86, 172, 5, {"biglaw": 5, "litigation": 4, "judicial-clerkship": 4, "judge": 4, "prosecutor": 3}),
    MockSchool(6, "NYU School of Law", "New York", "NY", 3.84, 171, 5, {"public-interest": 5, "biglaw": 4, "government": 4, "public-defender": 5, "litigation": 4}),
    MockSchool(7, "Penn Carey Law", "Philadelphia", "PA", 3.86, 171, 5, {"biglaw": 5, "litigation": 4, "judicial-clerkship": 4, "public-defender": 4, "judge": 3}),
    MockSchool(8, "University of Virginia School of Law", "Charlottesville", "VA", 3.88, 171, 4, {"government": 5, "judicial-clerkship": 5, "public-interest": 4, "judge": 5, "prosecutor": 4}),
    MockSchool(9, "University of Michigan Law School", "Ann Arbor", "MI", 3.82, 169, 4, {"biglaw": 4, "litigation": 4, "judicial-clerkship": 4, "public-defender": 4, "judge": 3}),
    MockSchool(10, "Duke University School of Law", "Durham", "NC", 3.85, 170, 4, {"biglaw": 4, "government": 4, "judicial-clerkship": 4, "judge": 4, "public-interest": 4}),
    MockSchool(11, "Northwestern Pritzker School of Law", "Chicago", "IL", 3.82, 168, 5, {"biglaw": 5, "litigation": 4, "government": 3, "judge": 3, "public-defender": 3}),
    MockSchool(12, "Cornell Law School", "Ithaca", "NY", 3.79, 169, 5, {"biglaw": 4, "judicial-clerkship": 4, "litigation": 4, "judge": 4, "public-interest": 3}),
    MockSchool(13, "Georgetown University Law Center", "Washington", "DC", 3.78, 168, 4, {"government": 5, "public-interest": 4, "prosecutor": 5, "public-defender": 4, "judge": 4}),
    MockSchool(14, "UCLA School of Law", "Los Angeles", "CA", 3.77, 168, 4, {"public-interest": 4, "litigation": 4, "government": 4, "public-defender": 5, "judge": 3}),
    MockSchool(15, "UC Berkeley School of Law", "Berkeley", "CA", 3.85, 170, 4, {"public-interest": 5, "biglaw": 4, "litigation": 4, "public-defender": 4, "judge": 4}),
    MockSchool(16, "University of Texas School of Law", "Austin", "TX", 3.75, 168, 3, {"government": 4, "biglaw": 4, "litigation": 4, "prosecutor": 5, "public-defender": 3}),
    MockSchool(17, "Vanderbilt Law School", "Nashville", "TN", 3.79, 166, 4, {"judicial-clerkship": 4, "litigation": 4, "government": 3, "judge": 4, "prosecutor": 3}),
    MockSchool(18, "Washington University School of Law", "St. Louis", "MO", 3.76, 167, 4, {"biglaw": 4, "judicial-clerkship": 4, "litigation": 4, "public-defender": 3, "judge": 3}),
    MockSchool(19, "USC Gould School of Law", "Los Angeles", "CA", 3.74, 166, 4, {"biglaw": 4, "litigation": 4, "entertainment-law": 4, "public-defender": 4, "judge": 3}),
    MockSchool(20, "University of Minnesota Law School", "Minneapolis", "MN", 3.73, 165, 3, {"government": 4, "public-interest": 4, "litigation": 4, "public-defender": 5, "judge": 4}),
)


def normalize_goal(goal: str) -> str:
    candidate = "-".join(part for part in goal.strip().lower().replace("&", " and ").split())
    return CAREER_ALIASES.get(goal.strip().lower(), CAREER_ALIASES.get(candidate, candidate))


def school_summary_dict(school: MockSchool) -> dict[str, object]:
    return {
        "id": school.school_id,
        "name": school.name,
        "city": school.city,
        "state": school.state,
    }