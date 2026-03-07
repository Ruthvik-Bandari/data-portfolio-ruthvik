.PHONY: setup ingest profile harmonize clean process combine validate export viz test lint format all

setup:
	uv sync --all-extras

ingest:
	uv run python -m src.ingest

profile:
	uv run python -m src.profile

harmonize:
	uv run python -m src.harmonize

clean:
	uv run python -m src.clean

combine:
	uv run python -m src.combine

validate:
	uv run python -m src.validate

export:
	uv run python -m src.export

viz:
	uv run python -m src.visualize

process: ingest profile harmonize clean combine validate export

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
	rm -rf data/interim/* data/processed/*
	@echo "Cleaned interim and processed data directories."

clean-all: clean-data
	rm -rf reports/data_quality_report.html reports/images/*.png
	@echo "Cleaned all generated outputs."
