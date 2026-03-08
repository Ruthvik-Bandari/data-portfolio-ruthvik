"""DuckDB powered aggregations for course review analytics."""

from __future__ import annotations

import duckdb
import polars as pl
from rich.console import Console

from src.config import AGGREGATED_DIR, PROCESSED_DIR

console = Console()


def run_aggregations() -> dict[str, pl.DataFrame]:
    """Run analytical aggregations using DuckDB.

    Returns:
        Dictionary of aggregation name to DataFrame.
    """
    AGGREGATED_DIR.mkdir(parents=True, exist_ok=True)

    df = pl.read_parquet(PROCESSED_DIR / "with_sentiment.parquet")
    conn = duckdb.connect()
    conn.register("reviews", df.to_pandas())

    results: dict[str, pl.DataFrame] = {}

    # 1. Sentiment by department
    console.print("  Aggregating: sentiment by department...")
    dept_sent = conn.execute("""
        SELECT department,
               COUNT(*) as review_count,
               AVG(rating) as avg_rating,
               AVG(sentiment_score) as avg_sentiment,
               SUM(CASE WHEN sentiment_label = 'POSITIVE' THEN 1 ELSE 0 END) as positive_count,
               SUM(CASE WHEN sentiment_label = 'NEGATIVE' THEN 1 ELSE 0 END) as negative_count
        FROM reviews
        GROUP BY department
        ORDER BY avg_sentiment DESC
    """).pl()
    results["dept_sentiment"] = dept_sent
    dept_sent.write_parquet(AGGREGATED_DIR / "dept_sentiment.parquet")

    # 2. Sentiment by department and aspect
    console.print("  Aggregating: sentiment by department x aspect...")
    aspect_cols = [c for c in df.columns if c.startswith("has_")]
    aspect_rows = []
    for col in aspect_cols:
        aspect_name = col.replace("has_", "")
        subset = df.filter(pl.col(col))
        if subset.height > 0:
            by_dept = (
                subset.group_by("department")
                .agg(
                    pl.col("sentiment_score").mean().alias("avg_sentiment"),
                    pl.len().alias("mention_count"),
                )
                .with_columns(pl.lit(aspect_name).alias("aspect"))
            )
            aspect_rows.append(by_dept)

    if aspect_rows:
        dept_aspect = pl.concat(aspect_rows)
        results["dept_aspect"] = dept_aspect
        dept_aspect.write_parquet(AGGREGATED_DIR / "dept_aspect_sentiment.parquet")

    # 3. Temporal trends
    console.print("  Aggregating: temporal trends...")
    temporal = conn.execute("""
        SELECT year, semester,
               COUNT(*) as review_count,
               AVG(rating) as avg_rating,
               AVG(sentiment_score) as avg_sentiment
        FROM reviews
        GROUP BY year, semester
        ORDER BY year, semester
    """).pl()
    results["temporal"] = temporal
    temporal.write_parquet(AGGREGATED_DIR / "temporal_trends.parquet")

    # 4. Rating vs sentiment alignment
    console.print("  Aggregating: rating vs sentiment...")
    alignment = conn.execute("""
        SELECT rating,
               AVG(sentiment_score) as avg_sentiment,
               COUNT(*) as count
        FROM reviews
        GROUP BY rating
        ORDER BY rating
    """).pl()
    results["alignment"] = alignment
    alignment.write_parquet(AGGREGATED_DIR / "rating_sentiment_alignment.parquet")

    conn.close()
    console.print(f"[green]Aggregations saved to {AGGREGATED_DIR}[/green]")
    return results


if __name__ == "__main__":
    console.print("[bold]DuckDB Aggregations[/bold]\n")
    results = run_aggregations()
    for name, df in results.items():
        console.print(f"  {name}: {df.height} rows")
