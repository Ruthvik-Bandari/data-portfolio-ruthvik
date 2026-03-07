"""Configuration for the text analytics pipeline."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"
PROCESSED_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_IMAGES_DIR = REPORTS_DIR / "images"

# BERTopic settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MIN_TOPIC_SIZE = 10
N_NEIGHBORS = 15
MIN_CLUSTER_SIZE = 10

# Portfolio colors
PORTFOLIO_COLORS = {
    "primary": "#2E75B6",
    "secondary": "#1B4F72",
    "accent": "#17A2B8",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "success": "#2ECC71",
    "text": "#2C3E50",
    "light": "#ECF0F1",
}

COLORWAY = [
    "#2E75B6",
    "#17A2B8",
    "#F39C12",
    "#E74C3C",
    "#2ECC71",
    "#9B59B6",
    "#1ABC9C",
    "#E67E22",
]
