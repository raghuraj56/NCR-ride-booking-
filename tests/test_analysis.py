"""Tests for the NCR ride bookings analysis pipeline.

Covers data loading, cleaning, date auto-detection, KPI math and
dashboard edge cases. Run with: pytest
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analysis_script import (  # noqa: E402
    CONFIG,
    calculate_kpis,
    clean_data,
    create_dashboard,
    feature_engineering,
    load_data,
    parse_dates,
)


def make_csv(path, dates, statuses, values, vehicles=None, columns=None):
    n = len(dates)
    if vehicles is None:
        vehicles = ["Auto"] * n
    df = pd.DataFrame(
        {
            "Booking ID": [f"BKG{i:04d}" for i in range(n)],
            "Customer ID": [f"C{i:04d}" for i in range(n)],
            "Date": dates,
            "Booking Status": statuses,
            "Vehicle Type": vehicles,
            "Booking Value": values,
        }
    )
    if columns:  # allow renaming columns, e.g. with stray whitespace
        df.columns = columns
    df.to_csv(path, index=False)
    return str(path)


# ── loading ─────────────────────────────────────────────────
def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_data(tmp_path / "nope.csv")


def test_load_missing_columns_raises(tmp_path):
    p = tmp_path / "bad.csv"
    pd.DataFrame({"A": [1]}).to_csv(p, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        load_data(p)


def test_load_strips_column_whitespace(tmp_path):
    # CSV exported from Excel often has padded headers
    cols = ["Booking ID", "Customer ID", " Date ", "Booking Status",
            "Vehicle Type", "Booking Value"]
    p = make_csv(tmp_path / "pad.csv", ["01/02/2024"], ["Completed"],
                 [100.0], columns=cols)
    df = load_data(p)  # should not raise
    assert set(["Date", "Booking Status"]).issubset(df.columns)


# ── date parsing ─────────────────────────────────────────────
def test_parse_dates_detects_day_first():
    s = pd.Series(["31/01/2024", "15/06/2024", "01/02/2024"])
    out = parse_dates(s)
    assert out.dt.day.tolist() == [31, 15, 1]
    assert out.notna().all()


def test_parse_dates_detects_month_first():
    s = pd.Series(["2024-01-31", "2024-06-15"])  # unambiguous ISO
    out = parse_dates(s)
    assert out.notna().all()


def test_parse_dates_coerces_garbage():
    s = pd.Series(["31/01/2024", "not a date"])
    out = parse_dates(s)
    assert out.notna().sum() == 1


# ── cleaning ─────────────────────────────────────────────────
def test_clean_maps_statuses_and_unknown(tmp_path):
    p = make_csv(
        tmp_path / "s.csv",
        ["01/01/2024"] * 5,
        ["Completed", "Cancelled by Customer", "Cancelled by Driver",
         "No Driver Found", "Driver Offline"],  # last one unknown
        [100.0] * 5,
    )
    df = clean_data(load_data(p))
    assert set(df["Status_Clean"]) == {"Completed", "Cancelled", "Other"}


def test_clean_drops_invalid_rows(tmp_path):
    p = make_csv(
        tmp_path / "s.csv",
        ["01/01/2024", "garbage", "01/01/2024"],
        ["Completed", "Completed", "Completed"],
        [100.0, 100.0, "not-a-number"],
    )
    df = clean_data(load_data(p))
    assert len(df) == 1


def test_clean_empty_after_drops_raises_clear_error(tmp_path):
    p = make_csv(tmp_path / "s.csv", ["garbage"], ["Completed"], [100.0])
    with pytest.raises(ValueError, match="after cleaning"):
        clean_data(load_data(p))


# ── KPI math ─────────────────────────────────────────────────
def _prepared(tmp_path, dates, statuses, values, vehicles=None):
    p = make_csv(tmp_path / "s.csv", dates, statuses, values, vehicles)
    df = clean_data(load_data(p))
    df = feature_engineering(df, CONFIG)
    return calculate_kpis(df, CONFIG)


def test_kpis_count_completed_revenue_only(tmp_path):
    kpis = _prepared(
        tmp_path,
        ["01/01/2024"] * 4,
        ["Completed", "Completed", "Cancelled by Customer", "Incomplete"],
        [100.0, 200.0, 999.0, 500.0],
    )
    # cancelled/incomplete fares must NOT inflate revenue
    assert kpis["revenue"] == pytest.approx(300.0)
    assert kpis["profit"] == pytest.approx(300.0 * 0.35)
    assert kpis["avg_revenue"] == pytest.approx(150.0)
    assert kpis["total"] == 4
    assert kpis["completed"] == 2
    assert kpis["cancelled"] == 1
    assert kpis["incomplete"] == 1


def test_cancellation_rate_excludes_incomplete(tmp_path):
    kpis = _prepared(
        tmp_path,
        ["01/01/2024"] * 5,
        ["Completed"] * 3 + ["Cancelled by Driver"] + ["Incomplete"],
        [100.0] * 5,
    )
    assert kpis["cancellation_rate"] == pytest.approx(25.0)  # 1/(3+1)


def test_potential_revenue_formula(tmp_path):
    kpis = _prepared(
        tmp_path,
        ["01/01/2024"] * 3,
        ["Completed", "Completed", "Cancelled by Customer"],
        [100.0, 300.0, 0.0],
    )
    # 1 cancelled * 0.5 * avg(100, 300) = 100
    assert kpis["potential_revenue"] == pytest.approx(100.0)


# ── dashboard edge cases ─────────────────────────────────────
def _make_dashboard(tmp_path, statuses, vehicles=None):
    dates = ["05/01/2024"] * len(statuses)
    values = [float(100 + i) for i in range(len(statuses))]
    p = make_csv(tmp_path / "s.csv", dates, statuses, values, vehicles)
    df = clean_data(load_data(p))
    df = feature_engineering(df, CONFIG)
    kpis = calculate_kpis(df, CONFIG)
    out = tmp_path / "dashboard.png"
    create_dashboard(df, kpis, str(out))
    return out


def test_dashboard_without_incomplete_rides(tmp_path):
    # statuses: Completed + Cancelled only — 'Incomplete' key absent
    # from value_counts(); list-indexing would raise KeyError
    statuses = ["Completed"] * 6 + ["Cancelled by Customer"] * 2
    out = _make_dashboard(tmp_path, statuses)
    assert out.exists() and out.stat().st_size > 0


def test_dashboard_with_no_completed_rides(tmp_path):
    # all rides cancelled — must fail with a clear message, not a
    # cryptic 'max() on empty slice'
    with pytest.raises(ValueError, match="completed"):
        _make_dashboard(tmp_path, ["No Driver Found"] * 4)


def test_dashboard_full_run(tmp_path):
    statuses = (["Completed"] * 10 + ["Cancelled by Customer"] * 3
                + ["Incomplete"] * 2)
    vehicles = (["Auto", "Bike", "Go Sedan"] * 5)[:15]
    out = _make_dashboard(tmp_path, statuses, vehicles)
    from PIL import Image
    img = Image.open(out)
    assert img.size[0] > 500
