"""Data ingestion — generates synthetic course review data.

Since course review datasets require scraping or Kaggle accounts,
this module generates realistic synthetic review data that
demonstrates the full aspect sentiment pipeline.
"""

from __future__ import annotations

import random

import polars as pl
from rich.console import Console

from src.config import PROCESSED_DIR

console = Console()

DEPARTMENTS = [
    "Computer Science",
    "Mathematics",
    "English",
    "Psychology",
    "Biology",
    "Business",
    "Engineering",
    "History",
    "Chemistry",
    "Economics",
    "Nursing",
    "Education",
]

COURSE_LEVELS = ["100-level", "200-level", "300-level", "400-level"]

POSITIVE_TEMPLATES = [
    "The {aspect} was excellent. {detail}",
    "Really impressed with the {aspect}. {detail}",
    "Outstanding {aspect} that made the course worthwhile. {detail}",
    "The {aspect} exceeded my expectations. {detail}",
    "I loved the {aspect} in this course. {detail}",
]

NEGATIVE_TEMPLATES = [
    "The {aspect} was disappointing. {detail}",
    "Poor {aspect} made the course frustrating. {detail}",
    "I was unhappy with the {aspect}. {detail}",
    "The {aspect} needs significant improvement. {detail}",
    "Really struggled with the {aspect}. {detail}",
]

NEUTRAL_TEMPLATES = [
    "The {aspect} was adequate. {detail}",
    "Average {aspect} for a course at this level. {detail}",
    "The {aspect} was neither great nor terrible. {detail}",
]

ASPECT_DETAILS = {
    "teaching quality": {
        "positive": [
            "The professor explained complex topics clearly.",
            "Lectures were engaging and well-organized.",
            "The instructor was always available for help.",
            "Best professor I have had at this university.",
        ],
        "negative": [
            "The lectures were disorganized and hard to follow.",
            "Professor seemed unprepared for class.",
            "Could not understand the instructor's explanations.",
            "The teaching style was monotonous and dull.",
        ],
    },
    "course content": {
        "positive": [
            "The material was relevant and up to date.",
            "Topics covered were directly applicable to my career.",
            "Well-structured curriculum with clear learning objectives.",
        ],
        "negative": [
            "The content felt outdated and irrelevant.",
            "Too much theory without practical application.",
            "Material did not align with course description.",
        ],
    },
    "workload": {
        "positive": [
            "Assignments were challenging but manageable.",
            "The workload was well-balanced throughout the semester.",
            "Projects were meaningful and not busywork.",
        ],
        "negative": [
            "Way too many assignments for a single course.",
            "The workload was overwhelming and unreasonable.",
            "Spent more time on this class than all others combined.",
        ],
    },
    "grading": {
        "positive": [
            "Fair grading with clear rubrics provided.",
            "Feedback on assignments was detailed and helpful.",
            "The grading scale was reasonable and transparent.",
        ],
        "negative": [
            "Grading felt arbitrary and inconsistent.",
            "No feedback provided on assignments.",
            "The curve was harsh and unfair.",
        ],
    },
    "engagement": {
        "positive": [
            "Class discussions were stimulating and inclusive.",
            "Interactive activities kept everyone involved.",
            "Group projects were well-designed and collaborative.",
        ],
        "negative": [
            "No class interaction, just passive listening.",
            "Group work was poorly organized.",
            "The course felt like a one-way lecture with no engagement.",
        ],
    },
}


def generate_review(review_id: int, rng: random.Random) -> dict:
    """Generate a single synthetic course review.

    Args:
        review_id: Unique review identifier.
        rng: Random number generator for reproducibility.

    Returns:
        Dictionary with review data.
    """
    department = rng.choice(DEPARTMENTS)
    level = rng.choice(COURSE_LEVELS)
    year = rng.randint(2020, 2024)
    semester = rng.choice(["Spring", "Fall"])
    rating = rng.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]

    # Generate review text from 1-3 aspects
    aspects_to_cover = rng.sample(list(ASPECT_DETAILS.keys()), k=rng.randint(1, 3))
    review_parts = []

    for aspect in aspects_to_cover:
        details = ASPECT_DETAILS[aspect]
        if rating >= 4:
            template = rng.choice(POSITIVE_TEMPLATES)
            detail = rng.choice(details["positive"])
        elif rating <= 2:
            template = rng.choice(NEGATIVE_TEMPLATES)
            detail = rng.choice(details["negative"])
        else:
            template = rng.choice(NEUTRAL_TEMPLATES)
            detail = rng.choice(details.get("positive", ["It was okay."]))

        review_parts.append(template.format(aspect=aspect, detail=detail))

    return {
        "review_id": review_id,
        "department": department,
        "course_level": level,
        "year": year,
        "semester": semester,
        "rating": rating,
        "review_text": " ".join(review_parts),
    }


def generate_dataset(n_reviews: int = 5000, seed: int = 42) -> pl.DataFrame:
    """Generate a synthetic course review dataset.

    Args:
        n_reviews: Number of reviews to generate.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with synthetic review data.
    """
    rng = random.Random(seed)
    reviews = [generate_review(i, rng) for i in range(n_reviews)]
    return pl.DataFrame(reviews)


if __name__ == "__main__":
    console.print("[bold]Course Review Data Generation[/bold]\n")

    df = generate_dataset(n_reviews=5000)
    console.print(f"Generated: {df.height:,} reviews")
    console.print(f"Departments: {df['department'].n_unique()}")
    console.print(f"Years: {df['year'].min()}-{df['year'].max()}")

    rating_dist = df.group_by("rating").len().sort("rating")
    console.print("\nRating distribution:")
    for row in rating_dist.iter_rows():
        console.print(f"  {row[0]} stars: {row[1]} ({row[1] / df.height * 100:.1f}%)")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.write_parquet(PROCESSED_DIR / "reviews.parquet")
    console.print(f"\n[green]Saved to {PROCESSED_DIR / 'reviews.parquet'}[/green]")
