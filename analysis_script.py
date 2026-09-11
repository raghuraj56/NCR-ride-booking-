"""NCR Ride Bookings — Data Analysis & BI Dashboard.

End-to-end pipeline: data loading, cleaning, feature engineering,
KPI calculation, dashboard generation and insight reporting.

Usage:
    python analysis_script.py [--data PATH] [--output PATH]

Defaults are relative to this file, so the script runs anywhere
(not just in Colab).
"""

import argparse
import os
import warnings

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # headless: works on servers / CI without a display
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Only suppress the specific noisy warnings we expect, not everything.
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

# ── 1. CONFIGURATION ────────────────────────────────────────
CONFIG = {
    "cost_ratio": 0.65,           # assumed operating cost as a share of revenue
    "target_cancellation_rate": 0.15,
    # Share of cancelled rides assumed recoverable (would have completed
    # and paid the average completed fare) if cancellations were reduced.
    "recoverable_cancel_share": 0.5,
}

COLORS = {
    "bg": "#0F1117",
    "card": "#1A1D27",
    "accent1": "#00D4FF",
    "accent2": "#A855F7",
    "green": "#10B981",
    "red": "#EF4444",
    "text": "#E2E8F0",
    "subtext": "#94A3B8",
    "grid": "#1E2235",
}

REQUIRED_COLUMNS = {
    "Date", "Booking ID", "Customer ID", "Booking Status",
    "Vehicle Type", "Booking Value",
}

STATUS_MAP = {
    "Completed": "Completed",
    "Cancelled by Customer": "Cancelled",
    "Cancelled by Driver": "Cancelled",
    "No Driver Found": "Cancelled",
    "Incomplete": "Incomplete",
}


# ── 2. DATA LOADING ────────────────────────────────────────
def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    df = pd.read_csv(path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    print(f"Data loaded: {df.shape}")
    return df


# ── 3. DATA CLEANING ────────────────────────────────────────
def parse_dates(series):
    """Parse dates, auto-detecting day-first vs month-first.

    A plain pd.to_datetime() call misparses or drops dd/mm/yyyy dates
    whose day is > 12 (e.g. 31/06/2024 becomes NaT). We try both
    conventions and keep whichever parses more values.
    """
    month_first = pd.to_datetime(series, errors="coerce")
    day_first = pd.to_datetime(series, errors="coerce", dayfirst=True)
    return day_first if day_first.notna().sum() > month_first.notna().sum() else month_first


def clean_data(df):
    df = df.copy()

    df["Date"] = parse_dates(df["Date"])

    df["Booking ID"] = df["Booking ID"].astype(str).str.replace('"', "").str.strip()
    df["Customer ID"] = df["Customer ID"].astype(str).str.replace('"', "").str.strip()

    unknown_status = set(df["Booking Status"].dropna()) - set(STATUS_MAP.keys())
    if unknown_status:
        print(f"Warning: unknown statuses found: {unknown_status}")

    df["Status_Clean"] = df["Booking Status"].map(STATUS_MAP).fillna("Other")

    df["Vehicle Type"] = df["Vehicle Type"].str.strip()
    df["Booking Value"] = pd.to_numeric(df["Booking Value"], errors="coerce")

    df = df.dropna(subset=["Date", "Booking Value"])

    return df


# ── 4. FEATURE ENGINEERING ────────────────────────────────────────
def feature_engineering(df, config):
    df = df.copy()

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%b")
    df["Period"] = df["Date"].dt.strftime("%Y-%m")  # unique per year+month

    df["Revenue"] = df["Booking Value"]
    df["Cost"] = df["Revenue"] * config["cost_ratio"]
    df["Profit"] = df["Revenue"] - df["Cost"]

    return df


# ── 5. KPI CALCULATIONS ────────────────────────────────────────
def calculate_kpis(df, config):
    """All monetary KPIs consider COMPLETED rides only.

    Cancellation rate = cancelled / (completed + cancelled).
    Incomplete rides are excluded from the denominator: a booking that
    started but did not finish is neither a completed sale nor a
    cancellation, and the recoverable-revenue estimate below relies on
    this definition.
    """
    total = len(df)
    completed = (df["Status_Clean"] == "Completed").sum()
    cancelled = (df["Status_Clean"] == "Cancelled").sum()
    incomplete = (df["Status_Clean"] == "Incomplete").sum()

    effective_total = completed + cancelled
    cancellation_rate = (cancelled / effective_total) * 100 if effective_total else 0

    # Revenue/profit are realised only when a ride completes.
    completed_df = df[df["Status_Clean"] == "Completed"]
    revenue = completed_df["Revenue"].sum()
    profit = completed_df["Profit"].sum()
    avg_rev = completed_df["Revenue"].mean() if len(completed_df) else 0

    # Estimated revenue recoverable by cutting cancellations.
    potential_revenue = (
        cancelled * config["recoverable_cancel_share"] * avg_rev
    )

    return {
        "total": total,
        "completed": completed,
        "cancelled": cancelled,
        "incomplete": incomplete,
        "cancellation_rate": cancellation_rate,
        "revenue": revenue,
        "profit": profit,
        "avg_revenue": avg_rev,
        "potential_revenue": potential_revenue,
    }


# ── 6. DASHBOARD ────────────────────────────────────────
def _style_axes(ax):
    ax.set_facecolor(COLORS["card"])
    ax.grid(color=COLORS["grid"], linestyle="--", linewidth=0.5)


def create_dashboard(df, kpis, output_path):
    plt.rcParams["text.color"] = COLORS["text"]
    plt.rcParams["axes.labelcolor"] = COLORS["text"]
    plt.rcParams["xtick.color"] = COLORS["subtext"]
    plt.rcParams["ytick.color"] = COLORS["subtext"]

    fig = plt.figure(figsize=(22, 13), facecolor=COLORS["bg"])
    gs = GridSpec(3, 3, figure=fig, height_ratios=[0.7, 2.0, 2.0])
    gs.update(hspace=0.55, wspace=0.30)  # headroom for rotated x-labels

    completed = df[df["Status_Clean"] == "Completed"]

    # ── 0. KPI HEADER ROW ────────────────────────────────
    kpi_cards = [
        ("Total Rides", f"{kpis['total']:,}"),
        ("Completed", f"{kpis['completed']:,}"),
        ("Cancellation Rate", f"{kpis['cancellation_rate']:.1f}%"),
        ("Revenue (Completed)", f"₹{kpis['revenue'] / 1e7:.2f} Cr"),
        ("Profit (Completed)", f"₹{kpis['profit'] / 1e7:.2f} Cr"),
        ("Avg Revenue / Ride", f"₹{kpis['avg_revenue']:,.0f}"),
    ]
    for i, (label, value) in enumerate(kpi_cards):
        axk = fig.add_subplot(gs[0, i // 2])
        axk.set_facecolor(COLORS["card"])
        axk.set_xticks([])
        axk.set_yticks([])
        for spine in axk.spines.values():
            spine.set_color(COLORS["grid"])
        axk.text(0.5, 0.62, label, ha="center", va="center",
                 fontsize=11, color=COLORS["subtext"], transform=axk.transAxes)
        axk.text(0.5, 0.28, value, ha="center", va="center",
                 fontsize=17, fontweight="bold",
                 color=COLORS["accent1"] if i % 2 == 0 else COLORS["accent2"],
                 transform=axk.transAxes)

    # ── 1. MONTHLY REVENUE & PROFIT (grouped bars) ─────────
    # Revenue = Cost + Profit, so profit is a SUBSET of revenue.
    # Grouped bars (not stacked) avoid visually inflating the totals.
    ax1 = fig.add_subplot(gs[1, :])

    monthly = (
        completed.groupby("Period")[["Revenue", "Profit"]]
        .sum()
        .sort_index()
        .reset_index()
    )
    x = np.arange(len(monthly))
    width = 0.38

    ax1.bar(x - width / 2, monthly["Revenue"], width,
            color=COLORS["accent1"], label="Revenue")
    ax1.bar(x + width / 2, monthly["Profit"], width,
            color=COLORS["accent2"], label="Profit")

    ax1.set_xticks(x)
    ax1.set_xticklabels(monthly["Period"], rotation=45, ha="right")
    ax1.set_title("Monthly Revenue & Profit — Completed Rides Only")
    ax1.set_ylabel("Amount (₹)")
    ax1.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"₹{v / 1e7:.0f} Cr")
    )
    ax1.legend(facecolor=COLORS["card"], edgecolor=COLORS["grid"],
               labelcolor=COLORS["text"])
    _style_axes(ax1)

    # ── 2. VEHICLE TYPE BAR CHART ─────────
    ax2 = fig.add_subplot(gs[2, 0])

    vehicle_summary = (
        completed.groupby("Vehicle Type")
        .agg(Rides=("Booking ID", "count"), Profit=("Profit", "sum"))
        .sort_values("Rides", ascending=True)
    )

    ax2.barh(vehicle_summary.index, vehicle_summary["Rides"], color=COLORS["accent2"])

    xmax = vehicle_summary["Rides"].max()
    ax2.set_xlim(0, xmax * 1.30)  # room so annotations never clip
    for i, (rides, profit) in enumerate(
        zip(vehicle_summary["Rides"], vehicle_summary["Profit"])
    ):
        ax2.text(rides + xmax * 0.015, i,
                 f"{rides:,} | ₹{profit / 1e5:.1f}L",
                 va="center", color=COLORS["text"], fontsize=9)

    ax2.set_title("Vehicle Type (Rides + Profit)")
    ax2.set_xlabel("Number of Rides")
    _style_axes(ax2)

    # ── 3. DONUT: PROFIT CONTRIBUTION ─────────
    ax3 = fig.add_subplot(gs[2, 1])

    profit_by_vehicle = vehicle_summary["Profit"]
    wedges, texts, autotexts = ax3.pie(
        profit_by_vehicle,
        labels=profit_by_vehicle.index,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.8,
    )

    centre_circle = plt.Circle((0, 0), 0.55, fc=COLORS["card"])
    ax3.add_artist(centre_circle)

    for t in texts + autotexts:
        t.set_color(COLORS["text"])

    ax3.set_title("Profit Contribution by Vehicle")
    ax3.set_facecolor(COLORS["card"])

    # ── 4. PIE: BOOKING STATUS ─────────
    ax4 = fig.add_subplot(gs[2, 2])

    status_counts = df["Status_Clean"].value_counts()
    top3 = status_counts[["Completed", "Cancelled", "Incomplete"]].fillna(0)

    labels = ["Completed", "Cancelled", "Incomplete"]
    colors = [COLORS["green"], COLORS["red"], COLORS["accent1"]]

    wedges, texts, autotexts = ax4.pie(
        top3.values, labels=labels, autopct="%1.1f%%",
        startangle=140, colors=colors,
    )

    for t in texts + autotexts:
        t.set_color(COLORS["text"])

    ax4.set_title("Booking Status Distribution")
    ax4.set_facecolor(COLORS["card"])

    # ── SAVE ───────────────────────────────────
    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)

    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    print(f"Dashboard saved at {output_path}")


# ── 7. INSIGHTS ────────────────────────────────────────
def generate_insights(kpis, config):
    print("\nKEY INSIGHTS")
    print("-" * 50)

    print(f"Total Rides               : {kpis['total']:,}")
    print(f"Completed / Cancelled / Incomplete: "
          f"{kpis['completed']:,} / {kpis['cancelled']:,} / {kpis['incomplete']:,}")
    print(f"Revenue (completed only)  : ₹{kpis['revenue']:,.0f}")
    print(f"Profit (completed only)   : ₹{kpis['profit']:,.0f}")
    print(f"Cancellation Rate         : {kpis['cancellation_rate']:.2f}% "
          f"(target: {config['target_cancellation_rate'] * 100:.0f}%)")
    print(f"Potential Revenue Gain    : ₹{kpis['potential_revenue']:,.0f} "
          f"(assumes {config['recoverable_cancel_share']:.0%} of cancelled "
          f"rides convert at avg revenue ₹{kpis['avg_revenue']:,.0f})")


# ── 8. MAIN PIPELINE ────────────────────────────────────────
def run_pipeline(data_path, output_path, config=CONFIG):
    df = load_data(data_path)
    df = clean_data(df)
    df = feature_engineering(df, config)
    kpis = calculate_kpis(df, config)

    create_dashboard(df, kpis, output_path)
    generate_insights(kpis, config)

    print("\nAnalysis Complete")
    return df, kpis


def parse_args():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="NCR ride bookings analysis")
    parser.add_argument("--data", default=os.path.join(here, "ncr_ride_bookings.csv"))
    parser.add_argument("--output", default=os.path.join(here, "outputs", "ncr_dashboard.png"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.data, args.output)
