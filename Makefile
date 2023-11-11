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