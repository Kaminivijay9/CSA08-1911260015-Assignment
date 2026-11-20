-- A1.2 storage design: one row per station, one row per hourly reading.
-- pm25 is NULL when the raw value was missing or impossible (see A2 rules).
CREATE TABLE IF NOT EXISTS stations (
    station_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS readings (
    reading_id INTEGER PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(station_id),
    ts         TEXT NOT NULL,          -- 'YYYY-MM-DD HH:MM'
    day        TEXT NOT NULL,          -- 'YYYY-MM-DD' for daily queries
    pm25       REAL,                   -- ug/m3, NULL if invalid
    temp_c     REAL,
    UNIQUE (station_id, ts)
);
CREATE INDEX IF NOT EXISTS idx_readings_station_day ON readings(station_id, day);
