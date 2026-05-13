CREATE TABLE IF NOT EXISTS job_postings (
    id              SERIAL PRIMARY KEY,
    job_title       VARCHAR(255) NOT NULL,
    company_name    VARCHAR(255),
    location        VARCHAR(255),
    is_remote       BOOLEAN DEFAULT FALSE,
    salary_min      NUMERIC(10,2),
    salary_max      NUMERIC(10,2),
    salary_type     VARCHAR(20),          -- 'hourly' | 'annual'
    raw_description TEXT,
    source_url      VARCHAR(1000),
    source          VARCHAR(50),          -- 'indeed'
    date_posted     DATE,
    scraped_at      TIMESTAMP DEFAULT NOW(),
    is_staffing_agency    BOOLEAN DEFAULT FALSE,
    agency_flag_reason    VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS job_skills (
    id               SERIAL PRIMARY KEY,
    job_id           INTEGER REFERENCES job_postings(id) ON DELETE CASCADE,
    skill_raw        VARCHAR(150),
    skill_normalized VARCHAR(100),
    skill_category   VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_postings_scraped   ON job_postings(scraped_at);
CREATE INDEX IF NOT EXISTS idx_postings_agency    ON job_postings(is_staffing_agency);
CREATE INDEX IF NOT EXISTS idx_skills_job_id      ON job_skills(job_id);
CREATE INDEX IF NOT EXISTS idx_skills_category    ON job_skills(skill_category);
