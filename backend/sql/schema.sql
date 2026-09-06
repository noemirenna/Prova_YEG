-- Schema PostgreSQL 16 per il progetto congresso.
-- Solo DDL: tabelle, vincoli e indici.

CREATE TABLE stakeholder_types (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE engagement_channels (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE participants (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    stakeholder_type_id INTEGER REFERENCES stakeholder_types(id),
    region_id INTEGER REFERENCES regions(id),
    engagement_channel_id INTEGER REFERENCES engagement_channels(id)
);

CREATE TABLE touchpoints (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    source_column TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phase TEXT NOT NULL CHECK (phase IN ('pre_event', 'on_site', 'session', 'post_event')),
    data_type TEXT NOT NULL CHECK (data_type IN ('boolean', 'integer', 'decimal', 'date'))
);

CREATE TABLE participant_touchpoints (
    participant_id INTEGER REFERENCES participants(id) ON DELETE CASCADE,
    touchpoint_id INTEGER REFERENCES touchpoints(id) ON DELETE CASCADE,
    value_boolean BOOLEAN,
    value_integer INTEGER,
    value_decimal NUMERIC(10,2),
    value_date DATE,
    PRIMARY KEY (participant_id, touchpoint_id)
);

CREATE INDEX idx_participants_email ON participants (email);
CREATE INDEX idx_participants_region_id ON participants (region_id);
CREATE INDEX idx_participants_stakeholder_type_id ON participants (stakeholder_type_id);
CREATE INDEX idx_participant_touchpoints_touchpoint_id ON participant_touchpoints (touchpoint_id);
CREATE INDEX idx_participant_touchpoints_participant_id ON participant_touchpoints (participant_id);
