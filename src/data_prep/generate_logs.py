"""
1.1 - Generation du dataset de logs (Melissa)

Simule des utilisateurs sur ~3 mois de logs (login / api / db),
avec des anomalies injectees volontairement (verite terrain connue)
pour pouvoir evaluer la detection plus tard (tests de Selma).

Colonnes :
user_id, timestamp, source, ip_address, country, city, device,
status, endpoint, query_type, session_duration,
ground_truth_anomaly, ground_truth_type

Sortie : data/raw/logs.csv et data/raw/logs.json
"""

import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

N_USERS = 300
N_DAYS = 90
ANOMALY_RATE = 0.05
RAW_DIR = "data/raw"

SOURCES = ["login", "api", "db"]
DEVICES = ["desktop", "mobile", "tablet"]
COUNTRIES = ["France", "Belgique", "Suisse", "Canada", "Maroc", "Algerie", "Tunisie"]
API_ENDPOINTS = ["/profile", "/orders", "/search", "/settings", "/admin", "/users/delete", "/config"]
DB_QUERIES = ["SELECT", "INSERT", "UPDATE", "DELETE"]
SENSITIVE_ENDPOINTS = ["/admin", "/users/delete", "/config"]


def build_user_profiles(n_users: int) -> list[dict]:
    """Cree un profil habituel par utilisateur : pays habituel, plage horaire habituelle, role."""
    profiles = []
    for i in range(n_users):
        profiles.append(
            {
                "user_id": f"user_{i:04d}",
                "usual_country": random.choice(COUNTRIES),
                "usual_hour_start": random.randint(6, 10),
                "usual_hour_end": random.randint(17, 22),
                "is_admin": random.random() < 0.1,  # 10% d'utilisateurs avec droits admin
            }
        )
    return profiles


def generate_normal_logs(n_users: int = N_USERS, n_days: int = N_DAYS) -> pd.DataFrame:
    """Genere les logs "normaux" : chaque utilisateur se connecte dans sa plage horaire
    habituelle, depuis son pays habituel, avec un taux d'echec faible."""
    profiles = build_user_profiles(n_users)
    start_date = datetime.now() - timedelta(days=n_days)

    rows = []
    for profile in profiles:
        # nombre de connexions sur la periode, variable par utilisateur
        n_sessions = random.randint(20, 80)
        for _ in range(n_sessions):
            day_offset = random.randint(0, n_days - 1)
            hour = random.randint(profile["usual_hour_start"], profile["usual_hour_end"])
            minute = random.randint(0, 59)
            timestamp = start_date + timedelta(days=day_offset, hours=hour, minutes=minute)

            source = random.choices(SOURCES, weights=[0.5, 0.35, 0.15])[0]
            status = "success" if random.random() > 0.05 else "fail"  # ~5% d'echecs normaux (mdp tape faux etc.)

            endpoint = random.choice(API_ENDPOINTS) if source == "api" else None
            # un utilisateur non-admin ne va normalement pas sur les endpoints sensibles
            if endpoint in SENSITIVE_ENDPOINTS and not profile["is_admin"]:
                endpoint = random.choice([e for e in API_ENDPOINTS if e not in SENSITIVE_ENDPOINTS])

            query_type = random.choice(DB_QUERIES) if source == "db" else None

            rows.append(
                {
                    "user_id": profile["user_id"],
                    "timestamp": timestamp,
                    "source": source,
                    "ip_address": fake.ipv4_public(),
                    "country": profile["usual_country"],
                    "city": fake.city(),
                    "device": random.choice(DEVICES),
                    "status": status,
                    "endpoint": endpoint,
                    "query_type": query_type,
                    "session_duration": round(random.uniform(10, 1800), 1),
                    "ground_truth_anomaly": 0,
                    "ground_truth_type": None,
                }
            )

    df = pd.DataFrame(rows)
    df.attrs["profiles"] = profiles  # garde les profils sous la main pour inject_anomalies
    return df.sort_values("timestamp").reset_index(drop=True)


def inject_anomalies(df: pd.DataFrame, rate: float = ANOMALY_RATE) -> pd.DataFrame:
    """Ajoute des lignes anormales de 4 types, avec ground_truth_anomaly=1
    et ground_truth_type renseigne, pour pouvoir evaluer la detection plus tard."""
    profiles = df.attrs.get("profiles", build_user_profiles(N_USERS))
    n_to_inject = int(len(df) * rate)
    n_per_type = max(1, n_to_inject // 4)
    new_rows = []

    # 1) brute_force : plusieurs echecs rapproches sur un meme compte
    for _ in range(n_per_type):
        profile = random.choice(profiles)
        base_time = fake.date_time_between(start_date="-90d", end_date="now")
        n_attempts = random.randint(5, 10)
        for i in range(n_attempts):
            new_rows.append(
                {
                    "user_id": profile["user_id"],
                    "timestamp": base_time + timedelta(minutes=i),
                    "source": "login",
                    "ip_address": fake.ipv4_public(),
                    "country": profile["usual_country"],
                    "city": fake.city(),
                    "device": random.choice(DEVICES),
                    "status": "fail",
                    "endpoint": None,
                    "query_type": None,
                    "session_duration": 0,
                    "ground_truth_anomaly": 1,
                    "ground_truth_type": "brute_force",
                }
            )

    # 2) unusual_hour : connexion en pleine nuit, hors plage habituelle
    for _ in range(n_per_type):
        profile = random.choice(profiles)
        base_date = fake.date_time_between(start_date="-90d", end_date="now")
        odd_hour = random.choice([1, 2, 3, 4])
        timestamp = base_date.replace(hour=odd_hour, minute=random.randint(0, 59))
        new_rows.append(
            {
                "user_id": profile["user_id"],
                "timestamp": timestamp,
                "source": "login",
                "ip_address": fake.ipv4_public(),
                "country": profile["usual_country"],
                "city": fake.city(),
                "device": random.choice(DEVICES),
                "status": "success",
                "endpoint": None,
                "query_type": None,
                "session_duration": round(random.uniform(10, 600), 1),
                "ground_truth_anomaly": 1,
                "ground_truth_type": "unusual_hour",
            }
        )

    # 3) impossible_travel : deux connexions dans des pays differents en tres peu de temps
    for _ in range(n_per_type):
        profile = random.choice(profiles)
        base_time = fake.date_time_between(start_date="-90d", end_date="now")
        other_country = random.choice([c for c in COUNTRIES if c != profile["usual_country"]])
        new_rows.append(
            {
                "user_id": profile["user_id"],
                "timestamp": base_time,
                "source": "login",
                "ip_address": fake.ipv4_public(),
                "country": profile["usual_country"],
                "city": fake.city(),
                "device": random.choice(DEVICES),
                "status": "success",
                "endpoint": None,
                "query_type": None,
                "session_duration": round(random.uniform(10, 600), 1),
                "ground_truth_anomaly": 0,
                "ground_truth_type": None,
            }
        )
        new_rows.append(
            {
                "user_id": profile["user_id"],
                "timestamp": base_time + timedelta(minutes=random.randint(2, 15)),
                "source": "login",
                "ip_address": fake.ipv4_public(),
                "country": other_country,
                "city": fake.city(),
                "device": random.choice(DEVICES),
                "status": "success",
                "endpoint": None,
                "query_type": None,
                "session_duration": round(random.uniform(10, 600), 1),
                "ground_truth_anomaly": 1,
                "ground_truth_type": "impossible_travel",
            }
        )

    # 4) unauthorized_access : endpoint sensible appele par un compte non-admin
    non_admin_profiles = [p for p in profiles if not p["is_admin"]] or profiles
    for _ in range(n_per_type):
        profile = random.choice(non_admin_profiles)
        timestamp = fake.date_time_between(start_date="-90d", end_date="now")
        new_rows.append(
            {
                "user_id": profile["user_id"],
                "timestamp": timestamp,
                "source": "api",
                "ip_address": fake.ipv4_public(),
                "country": profile["usual_country"],
                "city": fake.city(),
                "device": random.choice(DEVICES),
                "status": "success",
                "endpoint": random.choice(SENSITIVE_ENDPOINTS),
                "query_type": None,
                "session_duration": round(random.uniform(10, 600), 1),
                "ground_truth_anomaly": 1,
                "ground_truth_type": "unauthorized_access",
            }
        )

    df_anomalies = pd.DataFrame(new_rows)
    df_final = pd.concat([df, df_anomalies], ignore_index=True)
    return df_final.sort_values("timestamp").reset_index(drop=True)


def main():
    import os

    os.makedirs(RAW_DIR, exist_ok=True)

    df = generate_normal_logs()
    df = inject_anomalies(df)

    df.to_csv(f"{RAW_DIR}/logs.csv", index=False)
    df.to_json(f"{RAW_DIR}/logs.json", orient="records", date_format="iso")

    print(f"{len(df)} logs generes dans {RAW_DIR}/")
    print(f"Dont {df['ground_truth_anomaly'].sum()} anomalies injectees :")
    print(df[df['ground_truth_anomaly'] == 1]['ground_truth_type'].value_counts())


if __name__ == "__main__":
    main()