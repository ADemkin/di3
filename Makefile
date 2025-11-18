RUN := @uv run
SRC := di3
TESTS := tests

install:
	@uv sync

test:
	$(RUN) pytest $(TESTS) --cov=$(SRC) --cov-report=term-missing

ruff-check:
	@echo "ruff check:"
	$(RUN) ruff check $(SRC) $(TESTS)

ruff-fix:
	@echo "ruff fix:"
	$(RUN) ruff check --fix $(SRC) $(TESTS)

ruff-fmt:
	@echo "ruff fmt:"
	$(RUN) ruff format $(SRC) $(TESTS)

fmt: ruff-fix ruff-fmt

mypy:
	@echo "mypy:"
	$(RUN) mypy $(SRC) $(TESTS)

lint: ruff-check mypy

tox:
	@uv tool install tox
	@uv tool run tox run-parallel
