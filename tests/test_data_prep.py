"""
3.2 - Tests unitaires : nettoyage et feature engineering (Selma)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_prep.clean_data import clean_logs
from src.data_prep.features import add_time_features, add_rolling_failure_counts


def test_clean_logs_no_missing_ip():
    df = clean_logs()
    assert df["ip_address"].isna().sum() == 0


def test_clean_logs_no_duplicates():
    df = clean_logs()
    assert df.duplicated().sum() == 0


def test_time_features_hour_range():
    df = clean_logs()
    df = add_time_features(df)
    assert df["hour_of_day"].between(0, 23).all()


def test_time_features_day_of_week_range():
    df = clean_logs()
    df = add_time_features(df)
    assert df["day_of_week"].between(0, 6).all()


def test_rolling_failure_counts_non_negative():
    df = clean_logs()
    df = add_time_features(df)
    df = add_rolling_failure_counts(df)
    assert (df["fail_count_10min"] >= 0).all()
    assert (df["fail_count_1h"] >= df["fail_count_10min"]).all()