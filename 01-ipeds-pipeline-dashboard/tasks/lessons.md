# Lessons Learned — IPEDS Pipeline & Dashboard

## Session Log

## 2026-03-07 — Hatchling build failure + Python 3.14 incompatibility
**Mistake:** `make setup` failed with two errors: (1) hatchling couldn't find the package because `src/` doesn't match the project name `ipeds_pipeline_dashboard`, and (2) uv picked up Python 3.14 which Polars doesn't support yet.
**Root Cause:** Missing `[tool.hatch.build.targets.wheel] packages = ["src"]` in pyproject.toml, and `requires-python` was unbounded on the upper end (`>=3.12`).
**Rule:** Always add explicit hatch build config when using a `src/` layout that doesn't match the project name. Always upper bound `requires-python` to exclude unsupported Python versions.
**Applies To:** All projects (P1–P4) using hatchling + src/ layout
