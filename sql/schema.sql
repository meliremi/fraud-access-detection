-- 2.1 - Schema de la base (Selma) - SQLite
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    usual_country TEXT,
    usual_hour_start INTEGER,
    usual_hour_end INTEGER
);

CREATE TABLE IF NOT EXISTS logs (
    log_id INTEGER PRIMARY KEY,
    user_id TEXT,
    timestamp TEXT,
    source TEXT,
    ip_address TEXT,
    country TEXT,
    city TEXT,
    device TEXT,
    status TEXT,
    endpoint TEXT,
    query_type TEXT,
    session_duration REAL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS anomalies (
    log_id INTEGER,
    is_anomaly INTEGER,
    anomaly_score REAL,
    anomaly_type TEXT,
    anomaly_reason TEXT,
    detected_by TEXT,
    FOREIGN KEY (log_id) REFERENCES logs(log_id)
);