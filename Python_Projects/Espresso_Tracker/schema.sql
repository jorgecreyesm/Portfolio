-- Espresso Shot Tracker Schema
-- Run once: psql -d espresso -f schema.sql

CREATE TABLE IF NOT EXISTS beans (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    roaster      VARCHAR(100),
    roast_level  VARCHAR(20) CHECK (roast_level IN ('light', 'medium-light', 'medium', 'medium-dark', 'dark')),
    origin       VARCHAR(100),
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS shots (
    id            SERIAL PRIMARY KEY,
    shot_at       TIMESTAMP DEFAULT NOW(),
    bean_id       INTEGER REFERENCES beans(id),
    dose_g        NUMERIC(4,1) NOT NULL,
    yield_g       NUMERIC(4,1) NOT NULL,
    ratio         NUMERIC(4,2) GENERATED ALWAYS AS (yield_g / NULLIF(dose_g, 0)) STORED,
    time_sec      INTEGER NOT NULL,
    grind_setting VARCHAR(20),
    taste_rating  SMALLINT CHECK (taste_rating BETWEEN 1 AND 5),
    notes         TEXT
);
