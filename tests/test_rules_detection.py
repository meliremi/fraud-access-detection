"""
3.2 - Tests unitaires : regles de detection (Selma)

Cas limites : 0 echec, exactement au seuil, juste en dessous / au-dessus.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from src.detection.rules_detection import FAILED_ATTEMPTS_THRESHOLD, detect_brute_force


def make_df(fail_counts):
    return pd.DataFrame({"fail_count_10min": fail_counts})


def test_brute_force_zero_fails_not_flagged():
    df = detect_brute_force(make_df([0]))
    assert df["flag_brute_force"].iloc[0] == False


def test_brute_force_below_threshold_not_flagged():
    df = detect_brute_force(make_df([FAILED_ATTEMPTS_THRESHOLD - 1]))
    assert df["flag_brute_force"].iloc[0] == False


def test_brute_force_exactly_at_threshold_flagged():
    df = detect_brute_force(make_df([FAILED_ATTEMPTS_THRESHOLD]))
    assert df["flag_brute_force"].iloc[0] == True


def test_brute_force_above_threshold_flagged():
    df = detect_brute_force(make_df([FAILED_ATTEMPTS_THRESHOLD + 3]))
    assert df["flag_brute_force"].iloc[0] == True