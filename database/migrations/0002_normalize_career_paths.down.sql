DROP TABLE IF EXISTS user_profile_career_paths;
DROP TABLE IF EXISTS law_school_career_paths;
DROP TABLE IF EXISTS career_paths;

ALTER TABLE user_profiles
    ADD COLUMN IF NOT EXISTS career_goals TEXT[] NOT NULL DEFAULT '{}';