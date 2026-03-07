.PHONY: setup ingest features train explain viz export test lint format all

setup:
	uv sync --all-extras

ingest:
	uv run python -m src.ingest

features:
	uv run python -m src.features

train:
	uv run python -m src.model

explain:
	uv run python -m src.explain

viz:
	uv run python -m src.visualize

export:
	uv run python -m src.export

process: ingest features train explain export

all: process viz test

test:
	uv run pytest tests/ -v --tb=short

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

clean-data:
	rm -rf data/processed/* data/features/* models/*
	@echo "Cleaned processed data and models."
