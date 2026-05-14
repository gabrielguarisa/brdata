.PHONY: format
format:
	uvx ruff format .
	uvx ruff check .

.PHONY: test
test:
	uv run pytest