.PHONY: setup collect preprocess topics sentiment keywords viz export test lint format all

setup:
	uv sync --all-extras
	uv run python -m spacy download en_core_web_sm

collect:
	uv run python -m src.collect

preprocess:
	uv run python -m src.preprocess

topics:
	uv run python -m src.topics

sentiment:
	uv run python -m src.sentiment

keywords:
	uv run python -m src.keywords

viz:
	uv run python -m src.visualize

export:
	uv run python -m src.export

process: collect preprocess topics sentiment keywords export

all: process viz test

test:
	uv run pytest tests/ -v --tb=short

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/
