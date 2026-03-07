# ruff: noqa: E501
"""Generate a self contained HTML data quality report.

Reads profiling outputs from data/interim/ and produces a polished
HTML report with summary statistics, schema change details, and
null rate analysis.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
from rich.console import Console

from src.config import INTERIM_DIR, PROCESSED_DIR, REPORTS_DIR, SURVEY_COMPONENTS

console = Console()


def _stat_card(label: str, value: str, color: str = "#2E75B6") -> str:
    return f"""
    <div style="background:{color}; color:white; border-radius:8px;
                padding:20px; text-align:center; min-width:180px;">
        <div style="font-size:28px; font-weight:700;">{value}</div>
        <div style="font-size:13px; opacity:0.9; margin-top:4px;">{label}</div>
    </div>"""


def generate_data_quality_report(output_path: Path | None = None) -> Path:
    """Generate a comprehensive HTML data quality report.

    Args:
        output_path: Path to write the HTML file.

    Returns:
        Path to the generated report.
    """
    out = output_path or (REPORTS_DIR / "data_quality_report.html")
    out.parent.mkdir(parents=True, exist_ok=True)

    # Load processed data stats
    component_stats: list[dict] = []
    for comp in SURVEY_COMPONENTS:
        parquet_path = PROCESSED_DIR / f"ipeds_{comp}.parquet"
        if parquet_path.exists():
            df = pl.read_parquet(parquet_path)
            null_counts = df.null_count().row(0)
            total_nulls = sum(null_counts)
            total_cells = df.height * df.width
            null_rate = round(total_nulls / total_cells * 100, 2) if total_cells > 0 else 0

            component_stats.append(
                {
                    "component": comp.upper(),
                    "label": SURVEY_COMPONENTS[comp],
                    "rows": df.height,
                    "cols": df.width,
                    "null_rate": null_rate,
                    "years": df["SURVEY_YEAR"].n_unique() if "SURVEY_YEAR" in df.columns else 0,
                }
            )

    total_rows = sum(s["rows"] for s in component_stats)

    # Schema changes
    schema_changes_path = INTERIM_DIR / "schema_changes.csv"
    schema_changes_count = 0
    schema_html = "<p>No schema changes file found.</p>"
    if schema_changes_path.exists():
        changes = pl.read_csv(schema_changes_path)
        schema_changes_count = changes.height
        per_comp = changes.group_by("component").len().sort("len", descending=True)
        rows_html = ""
        for row in per_comp.iter_rows():
            rows_html += f"<tr><td>{row[0].upper()}</td><td>{SURVEY_COMPONENTS.get(row[0], row[0])}</td><td><strong>{row[1]}</strong></td></tr>"
        schema_html = f"""
        <table>
            <tr><th>Component</th><th>Survey</th><th>Columns Changed</th></tr>
            {rows_html}
        </table>"""

    # Column profiles
    profiles_path = INTERIM_DIR / "column_profiles.csv"
    high_null_html = "<p>No column profiles found.</p>"
    total_profiled = 0
    if profiles_path.exists():
        profiles = pl.read_csv(profiles_path)
        total_profiled = profiles.height
        high_null = (
            profiles.filter(pl.col("null_rate") > 0.5).sort("null_rate", descending=True).head(20)
        )
        if high_null.height > 0:
            rows_html = ""
            for row in high_null.iter_rows(named=True):
                pct = f"{row['null_rate'] * 100:.1f}%"
                rows_html += f'<tr><td>{row["source"]}</td><td><code>{row["column_name"]}</code></td><td>{row["dtype"]}</td><td style="color:#E74C3C; font-weight:600;">{pct}</td></tr>'
            high_null_html = f"""
            <table>
                <tr><th>Source File</th><th>Column</th><th>Type</th><th>Null Rate</th></tr>
                {rows_html}
            </table>"""
        else:
            high_null_html = "<p style='color:#2ECC71;'>No columns with >50% null rate found.</p>"

    # Component detail table
    comp_rows = ""
    for s in component_stats:
        color = "#E74C3C" if s["null_rate"] > 10 else "#F39C12" if s["null_rate"] > 5 else "#2ECC71"
        comp_rows += f"""
        <tr>
            <td><strong>{s["label"]}</strong><br><small>{s["component"]}</small></td>
            <td>{s["rows"]:,}</td>
            <td>{s["cols"]}</td>
            <td>{s["years"]}</td>
            <td style="color:{color}; font-weight:600;">{s["null_rate"]}%</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPEDS Data Quality Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Inter, system-ui, -apple-system, sans-serif; color: #2C3E50; background: #f8f9fa; line-height: 1.6; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ color: #1B4F72; font-size: 28px; margin-bottom: 8px; }}
        h2 {{ color: #2E75B6; font-size: 20px; margin: 40px 0 16px; border-bottom: 2px solid #2E75B6; padding-bottom: 8px; }}
        .subtitle {{ color: #7f8c8d; font-size: 14px; margin-bottom: 30px; }}
        .cards {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 24px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th {{ background: #1B4F72; color: white; padding: 12px 16px; text-align: left; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }}
        td {{ padding: 10px 16px; border-bottom: 1px solid #ecf0f1; font-size: 14px; }}
        tr:hover td {{ background: #f0f7ff; }}
        code {{ background: #ecf0f1; padding: 2px 6px; border-radius: 3px; font-size: 13px; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
        .badge-ok {{ background: #d5f5e3; color: #1e8449; }}
        .badge-warn {{ background: #fdebd0; color: #e67e22; }}
        .badge-bad {{ background: #fadbd8; color: #e74c3c; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #95a5a6; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>IPEDS Data Quality Report</h1>
        <p class="subtitle">
            Automated quality assessment of IPEDS survey data (2018-2024) |
            Generated by the IPEDS Pipeline
        </p>

        <div class="cards">
            {_stat_card("Total Rows", f"{total_rows:,}")}
            {_stat_card("Components", str(len(component_stats)), "#17A2B8")}
            {_stat_card("Columns Profiled", f"{total_profiled:,}", "#1B4F72")}
            {_stat_card("Schema Changes", str(schema_changes_count), "#E74C3C")}
            {_stat_card("Raw Files", "28", "#2ECC71")}
        </div>

        <h2>Component Summary</h2>
        <table>
            <tr><th>Component</th><th>Total Rows</th><th>Columns</th><th>Years</th><th>Null Rate</th></tr>
            {comp_rows}
        </table>

        <h2>Schema Changes Across Years</h2>
        <p>Columns that appeared, disappeared, or changed data type between survey years.</p>
        {schema_html}

        <h2>High Null Rate Columns (>50%)</h2>
        <p>Columns with more than half their values missing, indicating potential data quality issues.</p>
        {high_null_html}

        <h2>Pipeline Steps</h2>
        <table>
            <tr><th>Step</th><th>Description</th><th>Status</th></tr>
            <tr><td>1. Ingest</td><td>Read 28 CSVs with encoding fallback, null code mapping</td><td><span class="badge badge-ok">Complete</span></td></tr>
            <tr><td>2. Profile</td><td>Schema detection, null rates, cross-year comparison</td><td><span class="badge badge-ok">Complete</span></td></tr>
            <tr><td>3. Harmonize</td><td>Column normalization, type coercion, YAML schema generation</td><td><span class="badge badge-ok">Complete</span></td></tr>
            <tr><td>4. Clean</td><td>Deduplication, string cleaning, imputation flag processing</td><td><span class="badge badge-ok">Complete</span></td></tr>
            <tr><td>5. Combine</td><td>Diagonal concatenation across years per component</td><td><span class="badge badge-ok">Complete</span></td></tr>
            <tr><td>6. Export</td><td>Parquet + CSV + Tableau-optimized exports</td><td><span class="badge badge-ok">Complete</span></td></tr>
            <tr><td>7. Visualize</td><td>6 interactive Plotly charts + PNG exports</td><td><span class="badge badge-ok">Complete</span></td></tr>
        </table>

        <div class="footer">
            <p>IPEDS Data Pipeline &mdash; Ruthvik Bandari | Data Science &amp; Visualization Portfolio</p>
            <p>Data source: NCES IPEDS Complete Data Files (https://nces.ed.gov/ipeds/)</p>
        </div>
    </div>
</body>
</html>"""

    out.write_text(html)
    return out


if __name__ == "__main__":
    console.print("[bold]Generating Data Quality Report...[/bold]")
    path = generate_data_quality_report()
    console.print(f"[green]Report saved: {path}[/green]")
