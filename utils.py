"""
utils.py
--------
Small reusable helper functions shared by the Cluster dashboard and every
Unit dashboard: turning messy "Target" text into numbers, working out a
Red/Green style status, and formatting numbers nicely.
"""

import re
import pandas as pd


def _to_number(text):
    """Pulls the first number out of a string like '>=150/day' -> 150.0"""
    if text is None:
        return None
    match = re.search(r"[-+]?\d*\.?\d+", str(text).replace(",", ""))
    return float(match.group()) if match else None


def parse_target(target_text):
    """
    Splits a target string into (operator, number).
    Examples:
        '>=150/day'  -> ('>=', 150.0)
        '<=3.5 days' -> ('<=', 3.5)
        '<5%'        -> ('<', 5.0)
        '100%'       -> ('=', 100.0)
        'Monitor'    -> (None, None)   # not a numeric target
    """
    if target_text is None or str(target_text).strip().lower() in ("nan", "monitor", "track only", ""):
        return None, None

    text = str(target_text).strip()
    if text.startswith(">="):
        return ">=", _to_number(text)
    if text.startswith("<="):
        return "<=", _to_number(text)
    if text.startswith(">"):
        return ">", _to_number(text)
    if text.startswith("<"):
        return "<", _to_number(text)
    # A plain number or percentage like "100%" or a range like "1-5,00,000"
    number = _to_number(text)
    return ("=", number) if number is not None else (None, None)


def compute_status(today_value, target_text):
    """
    Compares today's value against the target and returns one of:
    'On Track', 'Off Track', 'No Data', 'Not Measurable'
    """
    today_number = _to_number(today_value)
    operator, target_number = parse_target(target_text)

    if today_number is None:
        return "No Data"
    if operator is None or target_number is None:
        return "Not Measurable"

    checks = {
        ">=": today_number >= target_number,
        "<=": today_number <= target_number,
        ">": today_number > target_number,
        "<": today_number < target_number,
        "=": today_number == target_number,
    }
    return "On Track" if checks.get(operator, False) else "Off Track"


STATUS_COLORS = {
    "On Track": "🟢",
    "Off Track": "🔴",
    "No Data": "⚪",
    "Not Measurable": "🔵",
}


def add_status_column(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a 'Status' column to a KPI dataframe based on Today vs Target."""
    df = df.copy()
    df["Status"] = df.apply(lambda row: compute_status(row.get("Today"), row.get("Target")), axis=1)
    df["Status Icon"] = df["Status"].map(STATUS_COLORS)
    return df


def department_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given the full master dataframe (already has a Status column),
    returns one row per department with counts of On Track / Off Track / No Data.
    """
    summary = (
        df.groupby("Department")["Status"]
        .value_counts()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ["On Track", "Off Track", "No Data", "Not Measurable"]:
        if col not in summary.columns:
            summary[col] = 0
    summary["Total KPIs"] = summary[["On Track", "Off Track", "No Data", "Not Measurable"]].sum(axis=1)
    return summary
