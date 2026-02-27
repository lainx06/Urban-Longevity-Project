"""
Urban Longevity - Phase 1: Data prep
Clean, filter (Manhattan only), and merge trees + air (PM2.5) + asthma by zip.
Output: one master dataset (zip-level) for Streamlit choropleth.
"""

import pandas as pd
from pathlib import Path

# --- Config: Manhattan zip range (10001 to 10282), file names ---
MANHATTAN_ZIP_MIN = 10001
MANHATTAN_ZIP_MAX = 10282
DATA_DIR = Path(__file__).resolve().parent


def _resolve_csv(path: Path) -> Path:
    """Use .csv file; if missing, try .csv.csv (workspace quirk)."""
    if path.exists():
        return path
    alt = path.parent / f"{path.stem}.csv.csv"
    return alt if alt.exists() else path


def load_trees() -> pd.DataFrame:
    """Load NYC Street Tree Census; filter to Manhattan only."""
    path = _resolve_csv(DATA_DIR / "trees.csv")
    df = pd.read_csv(path, low_memory=False)
    # Ensure postcode numeric for range filter
    df["postcode"] = pd.to_numeric(df["postcode"], errors="coerce")
    df = df.dropna(subset=["postcode"])
    mask = (df["borough"].str.strip().str.lower() == "manhattan") & (
        df["postcode"].ge(MANHATTAN_ZIP_MIN) & df["postcode"].le(MANHATTAN_ZIP_MAX)
    )
    return df.loc[mask].copy()


def load_air_pm25_manhattan() -> pd.DataFrame:
    """Load air quality; keep PM2.5 only; filter to Manhattan (Borough level)."""
    path = _resolve_csv(DATA_DIR / "air.csv")
    df = pd.read_csv(path, low_memory=False)
    pm25 = df["Name"].str.strip().str.lower().str.contains("fine particles.*pm 2.5", regex=True)
    measure_mean = df["Measure"].str.strip().str.lower() == "mean"
    manhattan = (
        (df["Geo Type Name"].str.strip() == "Borough")
        & (df["Geo Place Name"].str.strip().str.lower() == "manhattan")
    )
    out = df.loc[pm25 & measure_mean & manhattan].copy()
    out["Data Value"] = pd.to_numeric(out["Data Value"], errors="coerce")
    out = out.dropna(subset=["Data Value"])
    return out


def load_asthma_manhattan() -> pd.DataFrame:
    """Load asthma; filter to New York County (Manhattan)."""
    path = _resolve_csv(DATA_DIR / "asthma.csv")
    df = pd.read_csv(path, low_memory=False)
    ny_county = df["County"].str.strip().str.lower().str.contains("new york county")
    return df.loc[ny_county].copy()


def aggregate_trees_by_zip(trees: pd.DataFrame) -> pd.DataFrame:
    """One row per Manhattan zip: tree count and optional species summary."""
    trees = trees.astype({"postcode": int})
    by_zip = (
        trees.groupby("postcode", as_index=False)
        .agg(
            tree_count=("tree_id", "count"),
            # Keep one representative lat/lon per zip (e.g. median) for map
            latitude=("latitude", "median"),
            longitude=("longitude", "median"),
        )
        .rename(columns={"postcode": "zip"})
    )
    return by_zip


def get_latest_pm25(air: pd.DataFrame) -> float:
    """Single PM2.5 value for Manhattan (latest period). Prefer Annual over Summer."""
    air = air.copy()
    air["Start_Date"] = pd.to_datetime(air["Start_Date"], errors="coerce")
    air = air.dropna(subset=["Start_Date"])
    air = air.sort_values("Start_Date", ascending=False)
    # Prefer "Annual Average" if present
    annual = air[air["Time Period"].str.contains("Annual", case=False, na=False)]
    if not annual.empty:
        return float(annual.iloc[0]["Data Value"])
    return float(air.iloc[0]["Data Value"])


def get_latest_asthma_rate(asthma: pd.DataFrame) -> float:
    """Single asthma rate for Manhattan (latest year). Use cRate10K (per 10k)."""
    asthma = asthma.copy()
    # Use last 4 chars of Year as numeric if format like "2017-2019"
    asthma["YearEnd"] = asthma["Year"].astype(str).str.extract(r"(\d{4})$")[0]
    asthma["YearEnd"] = pd.to_numeric(asthma["YearEnd"], errors="coerce")
    asthma = asthma.dropna(subset=["YearEnd"])
    asthma = asthma.sort_values("YearEnd", ascending=False)
    return float(asthma.iloc[0]["cRate10K"])


def merge_master(
    trees_by_zip: pd.DataFrame,
    pm25_value: float,
    asthma_rate: float,
) -> pd.DataFrame:
    """Attach PM2.5 and asthma to zip-level tree table."""
    out = trees_by_zip.copy()
    out["pm25"] = pm25_value
    out["asthma_rate_per_10k"] = asthma_rate
    return out


def main():
    print("Loading trees (Manhattan only)...")
    trees = load_trees()
    print(f"  Manhattan tree rows: {len(trees)}")

    print("Loading air (PM2.5, Manhattan borough)...")
    air = load_air_pm25_manhattan()
    pm25 = get_latest_pm25(air)
    print(f"  Manhattan PM2.5 (latest): {pm25:.4f} mcg/m3")

    print("Loading asthma (New York County)...")
    asthma = load_asthma_manhattan()
    asthma_rate = get_latest_asthma_rate(asthma)
    print(f"  Manhattan asthma rate (latest): {asthma_rate:.2f} per 10k")

    print("Aggregating trees by zip...")
    trees_by_zip = aggregate_trees_by_zip(trees)
    print(f"  Manhattan zips with trees: {len(trees_by_zip)}")

    print("Merging into master dataset...")
    master = merge_master(trees_by_zip, pm25, asthma_rate)

    out_path = DATA_DIR / "manhattan_master.csv"
    master.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(master.head())
    return master


if __name__ == "__main__":
    main()
