RUN := @uv run
SRC := di3
TESTS := tests

.PHONY: install test lint fmt mypy ruff-check ruff-fix ruff-fmt tox

install:
	uv sync
	uv tool install tox

test:
	$(RUN) pytest $(TESTS) --cov=$(SRC) --cov-report=term-missing

ruff-check:
	$(RUN) ruff check $(SRC) $(TESTS)
	$(RUN) ruff format --check $(SRC) $(TESTS)

ruff-fix:
	$(RUN) ruff check --fix $(SRC) $(TESTS)

ruff-fmt:
	$(RUN) ruff format $(SRC) $(TESTS)

fmt: ruff-fix ruff-fmt

mypy:
	$(RUN) mypy $(SRC) $(TESTS)

lint: ruff-check mypy

tox:
	@uv tool run tox run-parallel
