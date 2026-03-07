"""ML model training and evaluation for earnings prediction."""

from __future__ import annotations

import json

import numpy as np
import polars as pl
import yaml
from rich.console import Console
from rich.table import Table
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from xgboost import XGBRegressor

from src.config import FEATURES_DIR, MODELS_DIR, REPORTS_DIR, TARGET

console = Console()


def load_ml_data() -> tuple[np.ndarray, np.ndarray, list[str], pl.DataFrame]:
    """Load feature matrix and target vector.

    Returns:
        Tuple of (X array, y array, feature names, full DataFrame).
    """
    df = pl.read_parquet(FEATURES_DIR / "scorecard_features.parquet")
    with open(FEATURES_DIR / "feature_columns.yaml") as f:
        config = yaml.safe_load(f)

    feature_cols = config["features"]

    # Fill remaining nulls with median for ML
    fill_exprs = [pl.col(c).fill_null(pl.col(c).median()) for c in feature_cols]
    df = df.with_columns(fill_exprs)

    x = df.select(feature_cols).to_numpy()
    y = df[TARGET].to_numpy().astype(float)

    return x, y, feature_cols, df


def train_and_evaluate() -> dict:
    """Train multiple models and compare performance.

    Returns:
        Dictionary with model results and the best model.
    """
    x, y, feature_cols, _df = load_ml_data()
    console.print(f"Training data: {x.shape[0]:,} samples, {x.shape[1]} features")

    # Replace any remaining NaN in X with 0
    x = np.nan_to_num(x, nan=0.0)

    models = {
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest": RandomForestRegressor(
            n_estimators=200, max_depth=15, random_state=42, n_jobs=-1
        ),
        "XGBoost": XGBRegressor(
            n_estimators=300, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1
        ),
    }

    results = {}
    table = Table(title="Model Comparison (5-Fold CV)")
    table.add_column("Model", style="bold")
    table.add_column("R2", justify="right")
    table.add_column("RMSE", justify="right")
    table.add_column("MAE", justify="right")

    best_score = -float("inf")
    best_name = ""

    for name, model in models.items():
        console.print(f"\n[blue]Training {name}...[/blue]")

        # Cross validation
        cv_r2 = cross_val_score(model, x, y, cv=5, scoring="r2")
        cv_rmse = -cross_val_score(model, x, y, cv=5, scoring="neg_root_mean_squared_error")
        cv_mae = -cross_val_score(model, x, y, cv=5, scoring="neg_mean_absolute_error")

        r2_mean = cv_r2.mean()
        rmse_mean = cv_rmse.mean()
        mae_mean = cv_mae.mean()

        results[name] = {
            "r2_mean": round(float(r2_mean), 4),
            "r2_std": round(float(cv_r2.std()), 4),
            "rmse_mean": round(float(rmse_mean), 0),
            "mae_mean": round(float(mae_mean), 0),
        }

        table.add_row(
            name,
            f"{r2_mean:.4f} +/- {cv_r2.std():.4f}",
            f"${rmse_mean:,.0f}",
            f"${mae_mean:,.0f}",
        )

        if r2_mean > best_score:
            best_score = r2_mean
            best_name = name

        # Fit on full data for later use
        model.fit(x, y)

    console.print()
    console.print(table)
    console.print(f"\n[green]Best model: {best_name} (R2 = {best_score:.4f})[/green]")

    # Save best model and results
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    import joblib

    best_model = models[best_name]
    joblib.dump(best_model, MODELS_DIR / "best_model.joblib")
    joblib.dump(feature_cols, MODELS_DIR / "feature_columns.joblib")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / "model_results.json", "w") as f:
        json.dump({"best_model": best_name, "results": results}, f, indent=2)

    return {
        "best_model": best_name,
        "best_score": best_score,
        "models": models,
        "X": x,
        "y": y,
        "features": feature_cols,
    }


if __name__ == "__main__":
    console.print("[bold]College Scorecard Model Training[/bold]\n")
    results = train_and_evaluate()
    console.print("\n[bold green]Training complete![/bold green]")
