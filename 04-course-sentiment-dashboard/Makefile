.PHONY: setup ingest aspects sentiment aggregate viz export test lint format all

setup:
	uv sync --all-extras

ingest:
	uv run python -m src.ingest

aspects:
	uv run python -m src.aspects

sentiment:
	uv run python -m src.sentiment

aggregate:
	uv run python -m src.aggregate

viz:
	uv run python -m src.visualize

export:
	uv run python -m src.export

process: ingest aspects sentiment aggregate export

all: process viz test

test:
	uv run pytest tests/ -v --tb=short

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/
