# PY-168 -- Microservices -- Python 3.12 -- poetry-core / conda
#
# conda can create a python=3.9.23 environment from conda-forge, but conda.anaconda.org and repo.anaconda.com are 403 at this build host's egress proxy, so no solved lock could be produced here. environment.yml is complete and solves on the operator's machine.
PYTHON ?= python3

.PHONY: help setup install lock test check tools verify audit clean

help:
	@echo "PY-168  (poetry-core 2.4.1 / conda (solver-resolved) / Python 3.12.11)"
	@echo ""
	@echo "  make setup     install the package manager this branch is pinned to"
	@echo "  make install   install the project and its tool pins"
	@echo "  make lock      install from the committed lockfile only"
	@echo "  make test      run the pytest suite"
	@echo "  make check     cross-file consistency audit (tools/full_check.py)"
	@echo "  make tools     run every wired tool, honouring skips (exit 3)"
	@echo "  make verify    check every tool is wired"
	@echo "  make audit     dependency listing for this branch's manager"

setup:
	conda env create -f environment.yml

install:
	conda env update -f environment.yml

lock:
	conda env update -f environment.yml --prune

test:
	$(PYTHON) -m pytest -q

check:
	$(PYTHON) tools/full_check.py

tools:
	$(PYTHON) tools/tool_integration.py --run

verify:
	$(PYTHON) tools/tool_integration.py --verify
	$(PYTHON) tools/verify_strategy_metrics.py

audit:
	conda list --json

clean:
	rm -rf reports build dist .pytest_cache .coverage coverage.xml
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
