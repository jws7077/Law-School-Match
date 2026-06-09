CREATE TABLE IF NOT EXISTS career_goals (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS schools (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    state CHAR(2) NOT NULL,
    tuition_in_state NUMERIC(10,2),
    tuition_out_state NUMERIC(10,2),
    ranking INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS school_career_focus (
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    career_goal_id INTEGER NOT NULL REFERENCES career_goals(id) ON DELETE CASCADE,
    focus_strength SMALLINT NOT NULL CHECK (focus_strength BETWEEN 1 AND 5),
    PRIMARY KEY (school_id, career_goal_id)
);

CREATE TABLE IF NOT EXISTS student_profiles (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE,
    gpa NUMERIC(3,2) NOT NULL CHECK (gpa BETWEEN 0.0 AND 4.0),
    lsat_score INTEGER NOT NULL CHECK (lsat_score BETWEEN 120 AND 180),
    geographic_preferences TEXT[] NOT NULL DEFAULT '{}',
    career_goals TEXT[] NOT NULL DEFAULT '{}',
    cost_sensitivity SMALLINT NOT NULL CHECK (cost_sensitivity BETWEEN 1 AND 5),
    lifestyle_preferences JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS match_results (
    id SERIAL PRIMARY KEY,
    student_profile_id INTEGER NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    match_score NUMERIC(5,2) NOT NULL CHECK (match_score BETWEEN 0 AND 100),
    score_breakdown JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (student_profile_id, school_id)
);

CREATE INDEX IF NOT EXISTS idx_schools_state ON schools(state);
CREATE INDEX IF NOT EXISTS idx_match_results_profile ON match_results(student_profile_id);
