DROP TABLE IF EXISTS aba_509_import_runs;

ALTER TABLE school_statistics
    DROP COLUMN IF EXISTS gpa_25th_percentile,
    DROP COLUMN IF EXISTS gpa_50th_percentile,
    DROP COLUMN IF EXISTS gpa_75th_percentile,
    DROP COLUMN IF EXISTS lsat_25th_percentile,
    DROP COLUMN IF EXISTS lsat_50th_percentile,
    DROP COLUMN IF EXISTS lsat_75th_percentile;