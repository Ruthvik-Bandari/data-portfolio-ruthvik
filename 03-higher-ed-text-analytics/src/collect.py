"""Data collection module for higher education research documents.

Collects abstracts from the ERIC (Education Resources Information Center)
database via their public API. ERIC is the primary database for education
research, maintained by IES (Institute of Education Sciences).
"""

from __future__ import annotations

import polars as pl
import requests
from rich.console import Console

from src.config import EXTRACTED_DIR

console = Console()

ERIC_API = "https://api.ies.ed.gov/eric/"


def search_eric(
    query: str,
    start: int = 0,
    rows: int = 200,
) -> list[dict]:
    """Search ERIC database for education research abstracts.

    Args:
        query: Search query string.
        start: Starting record number.
        rows: Number of results to return (max 200).

    Returns:
        List of document dictionaries with title, abstract, year, etc.
    """
    params = {
        "search": query,
        "start": start,
        "rows": min(rows, 200),
        "format": "json",
    }

    try:
        resp = requests.get(ERIC_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", {}).get("docs", [])
    except Exception as e:
        console.print(f"[yellow]ERIC API error: {e}[/yellow]")
        return []


def collect_higher_ed_abstracts(
    min_documents: int = 500,
) -> pl.DataFrame:
    """Collect higher education research abstracts from ERIC.

    Searches multiple higher ed topics to build a diverse corpus.

    Args:
        min_documents: Minimum number of documents to collect.

    Returns:
        DataFrame with columns: id, title, abstract, year, source, subject.
    """
    queries = [
        "higher education technology",
        "online learning university",
        "student success retention college",
        "AI artificial intelligence higher education",
        "college completion graduation",
        "higher education equity diversity",
        "university strategic planning",
        "higher education enrollment trends",
        "faculty development teaching",
        "higher education policy funding",
        "student mental health college",
        "higher education assessment outcomes",
    ]

    all_docs: list[dict] = []
    seen_ids: set[str] = set()

    for query in queries:
        if len(all_docs) >= min_documents:
            break

        console.print(f"  Searching: '{query}'...")

        for start in range(0, 200, 200):
            docs = search_eric(query, start=start, rows=200)
            if not docs:
                break

            for doc in docs:
                doc_id = doc.get("id", "")
                if doc_id in seen_ids or not doc.get("description"):
                    continue
                seen_ids.add(doc_id)

                all_docs.append(
                    {
                        "doc_id": doc_id,
                        "title": doc.get("title", ""),
                        "abstract": doc.get("description", ""),
                        "year": int(doc.get("publicationdateyear", 0))
                        if doc.get("publicationdateyear")
                        else None,
                        "source": doc.get("source", ""),
                        "subject": "; ".join(doc.get("subject", [])),
                        "author": "; ".join(doc.get("author", [])),
                        "pub_type": "; ".join(doc.get("publicationtype", [])),
                    }
                )

        console.print(f"    Collected so far: {len(all_docs)}")

    console.print(f"\n[green]Total documents collected: {len(all_docs)}[/green]")

    return pl.DataFrame(all_docs)


if __name__ == "__main__":
    console.print("[bold]Higher Ed Text Data Collection[/bold]\n")

    console.print("[bold]Collecting from ERIC database...[/bold]")
    df = collect_higher_ed_abstracts(min_documents=500)

    if df.height == 0:
        console.print("[red]No documents collected. Check your internet connection.[/red]")
        raise SystemExit(1)

    # Filter to recent years
    df = df.filter(pl.col("year").is_not_null() & (pl.col("year") >= 2018))
    console.print(f"After filtering to 2018+: {df.height} documents")

    # Save
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    df.write_parquet(EXTRACTED_DIR / "eric_abstracts.parquet")
    df.write_csv(EXTRACTED_DIR / "eric_abstracts.csv")
    console.print(f"[green]Saved to {EXTRACTED_DIR}[/green]")

    # Summary
    if "year" in df.columns:
        year_counts = df.group_by("year").len().sort("year")
        console.print("\nDocuments per year:")
        for row in year_counts.iter_rows():
            console.print(f"  {row[0]}: {row[1]}")
