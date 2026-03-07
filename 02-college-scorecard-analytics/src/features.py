"""Feature engineering pipeline for College Scorecard data."""

from __future__ import annotations

import polars as pl
from rich.console import Console

from src.config import (
    ADMISSIONS_COLS,
    COMPLETION_COLS,
    COST_COLS,
    DEMOGRAPHIC_COLS,
    FEATURES_DIR,
    INSTITUTION_COLS,
    OUTCOME_COLS,
    PROCESSED_DIR,
    TARGET,
)

console = Console()


def numeric_cast(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    """Cast columns to Float64, handling PrivacySuppressed and non numeric values.

    Args:
        df: Source DataFrame.
        columns: Columns to cast.

    Returns:
        DataFrame with numeric columns.
    """
    existing = [c for c in columns if c in df.columns]
    cast_exprs = [pl.col(c).cast(pl.Float64, strict=False) for c in existing]
    if cast_exprs:
        return df.with_columns(cast_exprs)
    return df


def select_feature_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Select and organize columns into feature groups.

    Args:
        df: Raw scorecard DataFrame.

    Returns:
        DataFrame with only relevant feature columns.
    """
    all_cols = (
        INSTITUTION_COLS
        + ADMISSIONS_COLS
        + COST_COLS
        + COMPLETION_COLS
        + DEMOGRAPHIC_COLS
        + OUTCOME_COLS
    )
    existing = [c for c in all_cols if c in df.columns]
    return df.select(existing)


def engineer_features(df: pl.DataFrame) -> pl.DataFrame:
    """Create engineered features from raw scorecard data.

    Features created:
    - selectivity_index: ADM_RATE * SAT_AVG (lower = more selective)
    - cost_burden: NPT4_PUB or NPT4_PRIV normalized
    - completion_efficiency: C150_4 / RET_FT4
    - diversity_index: Herfindahl index on demographic shares

    Args:
        df: DataFrame with numeric feature columns.

    Returns:
        DataFrame with additional engineered columns.
    """
    exprs = []

    # Selectivity index
    if "ADM_RATE" in df.columns and "SAT_AVG" in df.columns:
        exprs.append((pl.col("ADM_RATE") * pl.col("SAT_AVG")).alias("SELECTIVITY_INDEX"))

    # Completion efficiency
    if "C150_4" in df.columns and "RET_FT4" in df.columns:
        exprs.append(
            (pl.col("C150_4") / pl.col("RET_FT4").replace(0, None)).alias("COMPLETION_EFFICIENCY")
        )

    # Diversity index (1 - Herfindahl): higher = more diverse
    demo_share_cols = [
        "UGDS_WHITE",
        "UGDS_BLACK",
        "UGDS_HISP",
        "UGDS_ASIAN",
        "UGDS_AIAN",
        "UGDS_NHPI",
        "UGDS_2MOR",
        "UGDS_NRA",
        "UGDS_UNKN",
    ]
    existing_demo = [c for c in demo_share_cols if c in df.columns]
    if len(existing_demo) >= 4:
        hhi_expr = sum(pl.col(c).pow(2) for c in existing_demo)
        exprs.append((1 - hhi_expr).alias("DIVERSITY_INDEX"))

    # Student size category
    if "UGDS" in df.columns:
        exprs.append(
            pl.when(pl.col("UGDS") < 1000)
            .then(pl.lit("Small"))
            .when(pl.col("UGDS") < 5000)
            .then(pl.lit("Medium"))
            .when(pl.col("UGDS") < 15000)
            .then(pl.lit("Large"))
            .otherwise(pl.lit("Very Large"))
            .alias("SIZE_CATEGORY")
        )

    if exprs:
        df = df.with_columns(exprs)
    return df


def prepare_ml_dataset(df: pl.DataFrame) -> tuple[pl.DataFrame, list[str]]:
    """Prepare the final ML ready dataset.

    Drops rows without target, selects numeric features,
    and returns feature names.

    Args:
        df: Engineered DataFrame.

    Returns:
        Tuple of (ML ready DataFrame, list of feature column names).
    """
    # Must have target
    if TARGET not in df.columns:
        msg = f"Target column {TARGET} not found"
        raise ValueError(msg)

    # Filter to rows with target
    df = df.filter(pl.col(TARGET).is_not_null())

    # Select numeric columns as features (exclude identifiers and target)
    exclude = {"UNITID", "INSTNM", "STABBR", TARGET, "SIZE_CATEGORY", "OPEID", "OPEID6"}
    feature_cols = [
        c
        for c in df.columns
        if df[c].dtype in (pl.Float64, pl.Int64)
        and c not in exclude
        and df[c].null_count() / df.height < 0.4  # Drop features with >40% null
    ]

    console.print(f"  Features selected: {len(feature_cols)}")
    console.print(f"  Rows with target: {df.height:,}")

    return df, feature_cols


if __name__ == "__main__":
    console.print("[bold]College Scorecard Feature Engineering[/bold]\n")

    # Load raw
    raw_path = PROCESSED_DIR / "scorecard_raw.parquet"
    if not raw_path.exists():
        console.print("[red]Run `make ingest` first[/red]")
        raise SystemExit(1)

    df = pl.read_parquet(raw_path)
    console.print(f"Loaded: {df.height:,} rows x {df.width:,} cols")

    # Select features
    console.print("\n[bold]Selecting feature columns...[/bold]")
    df = select_feature_columns(df)
    console.print(f"  Selected: {df.width} columns")

    # Cast to numeric
    console.print("\n[bold]Casting to numeric...[/bold]")
    num_cols = ADMISSIONS_COLS + COST_COLS + COMPLETION_COLS + DEMOGRAPHIC_COLS + OUTCOME_COLS
    df = numeric_cast(df, num_cols)

    # Engineer features
    console.print("\n[bold]Engineering features...[/bold]")
    df = engineer_features(df)

    # Prepare ML dataset
    console.print("\n[bold]Preparing ML dataset...[/bold]")
    df, feature_cols = prepare_ml_dataset(df)

    # Save
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    df.write_parquet(FEATURES_DIR / "scorecard_features.parquet")
    console.print(f"\n[green]Saved features: {FEATURES_DIR / 'scorecard_features.parquet'}[/green]")

    # Save feature list
    import yaml

    with open(FEATURES_DIR / "feature_columns.yaml", "w") as f:
        yaml.dump({"target": TARGET, "features": feature_cols}, f)
    console.print(f"[green]Feature list: {FEATURES_DIR / 'feature_columns.yaml'}[/green]")
