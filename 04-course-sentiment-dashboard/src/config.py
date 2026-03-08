"""Configuration for the course sentiment pipeline."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
AGGREGATED_DIR = DATA_DIR / "aggregated"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_IMAGES_DIR = REPORTS_DIR / "images"

ASPECT_CATEGORIES = {
    "teaching_quality": [
        "instructor",
        "teacher",
        "professor",
        "teaching",
        "lecture",
        "explain",
        "helpful",
        "knowledgeable",
        "engaging",
        "boring",
    ],
    "course_content": [
        "content",
        "material",
        "curriculum",
        "topic",
        "subject",
        "relevant",
        "outdated",
        "interesting",
        "useful",
        "practical",
    ],
    "workload": [
        "workload",
        "assignment",
        "homework",
        "project",
        "exam",
        "heavy",
        "light",
        "manageable",
        "overwhelming",
        "time",
    ],
    "grading": [
        "grade",
        "grading",
        "fair",
        "harsh",
        "rubric",
        "feedback",
        "score",
        "assessment",
        "test",
        "quiz",
    ],
    "accessibility": [
        "accessible",
        "online",
        "flexible",
        "accommodate",
        "disability",
        "support",
        "resource",
        "available",
        "office hours",
        "responsive",
    ],
    "engagement": [
        "engage",
        "interactive",
        "discussion",
        "participate",
        "collaborate",
        "group",
        "peer",
        "activity",
        "hands-on",
        "boring",
    ],
}

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
