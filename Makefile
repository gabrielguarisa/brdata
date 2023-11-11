.PHONY: init
init:
	poetry install -n

.PHONY: formatting
formatting:
	poetry run ruff format .

.PHONY: linting
linting:
	poetry run ruff check .

.PHONY: tests
tests:
	poetry run pytest

.PHONY: tests-offline
tests-offline:
	poetry run pytest -m offline

.PHONY: tests-online
tests-online:
	poetry run pytest -m online