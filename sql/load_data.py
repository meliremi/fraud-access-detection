"""
2.2 - Import des donnees dans SQLite (Selma)

Charge data/processed/logs_scored.csv dans une base SQLite en suivant
le schema defini dans sql/schema.sql.
"""
import os
import sqlite3
import pandas as pd

DB_PATH = "sql/fraud_detection.db"
SCHEMA_PATH = "sql/schema.sql"
DATA_PATH = "data/processed/logs_scored.csv"


def create_schema(conn: sqlite3.Connection):
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())


def load_logs(conn: sqlite3.Connection):
    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])

    # table users : un profil par utilisateur
    users = (
        df.groupby("user_id")
        .agg(
            usual_country=("usual_country", "first"),
            usual_hour_start=("usual_hour_mean", lambda x: int(round(x.min()))),
            usual_hour_end=("usual_hour_mean", lambda x: int(round(x.max()))),
        )
        .reset_index()
    )
    users.to_sql("users", conn, if_exists="append", index=False)

    # table logs
    logs_cols = [
        "user_id", "timestamp", "source", "ip_address", "country", "city",
        "device", "status", "endpoint", "query_type", "session_duration",
    ]
    logs = df[logs_cols].copy()
    logs.insert(0, "log_id", range(1, len(logs) + 1))
    logs.to_sql("logs", conn, if_exists="append", index=False)

    # table anomalies
    anomalies = df[["is_anomaly", "anomaly_score", "anomaly_type", "anomaly_reason", "detected_by"]].copy()
    anomalies.insert(0, "log_id", range(1, len(anomalies) + 1))
    anomalies.to_sql("anomalies", conn, if_exists="append", index=False)

    print(f"{len(logs)} logs et {len(anomalies)} anomalies charges dans {DB_PATH}")


def main():
    # on repart d'une base propre a chaque execution pour eviter les doublons
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)
    load_logs(conn)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()