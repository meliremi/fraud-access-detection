"""
7. Bonus - Systeme d'alertes (Selma)

Scanne data/processed/logs_scored.csv et declenche une alerte (log fichier + print)
des qu'une anomalie critique (brute_force ou unauthorized_access) apparait.
Pas d'interface : uniquement backend.
"""
import pandas as pd
from datetime import datetime

DATA_PATH = "data/processed/logs_scored.csv"
ALERT_LOG_PATH = "src/alerts/alerts.log"

CRITICAL_ANOMALY_TYPES = ["brute_force", "unauthorized_access"]


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["timestamp"])


def find_critical_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Filtre les lignes correspondant a une anomalie critique."""
    mask = (df["is_anomaly"] == 1) & (df["anomaly_type"].isin(CRITICAL_ANOMALY_TYPES))
    return df[mask]


def format_alert(row: pd.Series) -> str:
    return (
        f"[ALERTE CRITIQUE] {datetime.now().isoformat()} | "
        f"user_id={row['user_id']} | type={row['anomaly_type']} | "
        f"source={row.get('source', 'N/A')} | "
        f"timestamp_log={row['timestamp']} | "
        f"score={row.get('anomaly_score', 'N/A')}"
    )


def trigger_alerts(critical_df: pd.DataFrame, log_path: str = ALERT_LOG_PATH):
    with open(log_path, "a", encoding="utf-8") as f:
        for _, row in critical_df.iterrows():
            message = format_alert(row)
            print(message)
            f.write(message + "\n")


def main():
    df = load_data()
    critical = find_critical_anomalies(df)
    print(f"{len(critical)} anomalie(s) critique(s) detectee(s) sur {len(df)} logs.\n")
    trigger_alerts(critical)
    print(f"\nAlertes ecrites dans {ALERT_LOG_PATH}")


if __name__ == "__main__":
    main()