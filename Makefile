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

.PHONY: docs
docs:
	poetry run lazydocs --src-base-url="https://github.com/gabrielguarisa/brdata/blob/main/" brdata --overview-file="README.md"

.PHONY: clear-docs
clear-docs:
	rm -rf docs