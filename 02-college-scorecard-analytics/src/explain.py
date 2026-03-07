"""SHAP explainability analysis for the earnings prediction model."""

from __future__ import annotations

import numpy as np
import polars as pl
import shap
import yaml
from rich.console import Console

from src.config import FEATURES_DIR, MODELS_DIR, REPORTS_DIR, REPORTS_IMAGES_DIR

console = Console()


def run_shap_analysis() -> None:
    """Run SHAP analysis on the best model and generate plots."""
    import joblib
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    REPORTS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Load model and data
    model = joblib.load(MODELS_DIR / "best_model.joblib")
    feature_cols = joblib.load(MODELS_DIR / "feature_columns.joblib")

    df = pl.read_parquet(FEATURES_DIR / "scorecard_features.parquet")
    fill_exprs = [pl.col(c).fill_null(pl.col(c).median()) for c in feature_cols]
    df = df.with_columns(fill_exprs)
    x = df.select(feature_cols).to_numpy()
    x = np.nan_to_num(x, nan=0.0)

    console.print(f"Computing SHAP values for {x.shape[0]:,} samples, {x.shape[1]} features...")

    # Use TreeExplainer for tree models
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x)

    console.print("[green]SHAP values computed![/green]")

    # Summary plot (beeswarm)
    console.print("\nGenerating SHAP summary plot...")
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, x, feature_names=feature_cols, show=False, max_display=20)
    plt.tight_layout()
    plt.savefig(REPORTS_IMAGES_DIR / "shap_summary.png", dpi=200, bbox_inches="tight")
    plt.close()
    console.print(f"  Saved: {REPORTS_IMAGES_DIR / 'shap_summary.png'}")

    # Bar plot (mean absolute SHAP)
    console.print("Generating SHAP importance bar plot...")
    plt.figure(figsize=(12, 8))
    shap.summary_plot(
        shap_values, x, feature_names=feature_cols, plot_type="bar", show=False, max_display=20
    )
    plt.tight_layout()
    plt.savefig(REPORTS_IMAGES_DIR / "shap_importance.png", dpi=200, bbox_inches="tight")
    plt.close()
    console.print(f"  Saved: {REPORTS_IMAGES_DIR / 'shap_importance.png'}")

    # Top features
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_indices = np.argsort(mean_abs_shap)[::-1][:15]
    top_features = [(feature_cols[i], float(mean_abs_shap[i])) for i in top_indices]

    console.print("\n[bold]Top 15 Features by SHAP Importance:[/bold]")
    for i, (feat, importance) in enumerate(top_features, 1):
        console.print(f"  {i:2d}. {feat}: {importance:.1f}")

    # Save top features
    with open(REPORTS_DIR / "shap_top_features.yaml", "w") as f:
        yaml.dump(
            {"top_features": [{"name": n, "importance": round(v, 2)} for n, v in top_features]}, f
        )


if __name__ == "__main__":
    console.print("[bold]SHAP Explainability Analysis[/bold]\n")
    run_shap_analysis()
    console.print("\n[bold green]SHAP analysis complete![/bold green]")
